import aioble
import asyncio
import bluetooth
import os
import struct
import sys


sys.path.insert(0, "/system/apps/mqttooth")
os.chdir("/system/apps/mqttooth")


class SensorError:
    def __init__(self, msg: str):
        self.msg = msg

    def message(self) -> str:
        return self.msg


SensorError.SENSOR_NOT_FOUND = SensorError("Sensor not found")
SensorError.CONNECTION_TIMEOUT = SensorError("Connection timed out")
SensorError.SERVICE_NOT_FOUND = SensorError("Service not found")


class GattError:
    def __init__(self, code: int):
        self.code = code

    def __eq__(self, other: object) -> bool:
        return isinstance(other, GattError) and self.code == other.code

    def message(self) -> str:
        if self.code == 1:
            return "Device disconnected"
        if self.code == 6:
            return "Device not ready"
        return f"GATT error ({self.code})"


class SensorData:
    TEMPERATURE_THRESHOLD = 0.1  # °C
    HUMIDITY_THRESHOLD = 1.0  # %RH

    def __init__(self, temperature: float, humidity: float):
        self.temperature = temperature
        self.humidity = humidity

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, SensorData)
            and abs(self.temperature - other.temperature) < self.TEMPERATURE_THRESHOLD
            and abs(self.humidity - other.humidity) < self.HUMIDITY_THRESHOLD
        )


# org.bluetooth.service.environmental_sensing
_ENV_SENSE_UUID = bluetooth.UUID(0x181A)
# org.bluetooth.characteristic.temperature
_ENV_SENSE_TEMPERATURE_UUID = bluetooth.UUID(0x2A6E)
# org.bluetooth.characteristic.humidity
_ENV_SENSE_HUMIDITY_UUID = bluetooth.UUID(0x2A6F)

_DEVICE_NAME = "mqttooth"


def _decode_temperature(data: bytes) -> float:
    return struct.unpack("<h", data)[0] / 100


def _decode_humidity(data: bytes) -> float:
    return struct.unpack("<H", data)[0] / 100


async def fetch_sensor_data() -> SensorData | SensorError | GattError:
    async with aioble.scan(
        5000, interval_us=250000, window_us=250000, active=True
    ) as scanner:
        async for result in scanner:
            if result.name() == _DEVICE_NAME and _ENV_SENSE_UUID in result.services():
                device = result.device
                break
        else:
            return SensorError.SENSOR_NOT_FOUND

    try:
        connection = await device.connect()
        async with connection:
            env_service = await connection.service(_ENV_SENSE_UUID)
            if env_service is None:
                return SensorError.SERVICE_NOT_FOUND

            temperature_char = await env_service.characteristic(
                _ENV_SENSE_TEMPERATURE_UUID
            )
            humidity_char = await env_service.characteristic(_ENV_SENSE_HUMIDITY_UUID)
            if temperature_char is None or humidity_char is None:
                return SensorError.SERVICE_NOT_FOUND

            temperature = _decode_temperature(await temperature_char.read())
            humidity = _decode_humidity(await humidity_char.read())
            return SensorData(temperature, humidity)
    except asyncio.TimeoutError:
        return SensorError.CONNECTION_TIMEOUT
    except aioble.GattError as exception:
        return GattError(exception.args[0])


class AppState:
    FULL_UPDATE_INTERVAL = 10

    def __init__(
        self,
        data: SensorData | None = None,
        fetch_time: tuple | None = None,
        error: SensorError | GattError | None = None,
        update_count: int = 0,
    ):
        self.data = data
        self.fetch_time = fetch_time
        self.error = error
        self.update_count = update_count

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, AppState)
            and self.data == other.data
            and self.error == other.error
        )

    def update_mode(self) -> int:
        if self.update_count % self.FULL_UPDATE_INTERVAL == 0:
            return FULL_UPDATE
        return MEDIUM_UPDATE

    def to_dict(self) -> dict:
        data = None
        if self.data:
            data = {
                "temperature": self.data.temperature,
                "humidity": self.data.humidity,
            }
        error = None
        if self.error:
            if isinstance(self.error, GattError):
                error = {"type": "GattError", "code": self.error.code}
            else:
                error = {"type": "SensorError", "msg": self.error.msg}
        return {
            "data": data,
            "fetch_time": self.fetch_time,
            "error": error,
            "update_count": self.update_count,
        }

    @classmethod
    def from_dict(cls, state_dict: dict) -> "AppState":
        data = None
        if state_dict.get("data"):
            d = state_dict["data"]
            data = SensorData(d["temperature"], d["humidity"])
        error = None
        if state_dict.get("error"):
            err = state_dict["error"]
            if err["type"] == "GattError":
                error = GattError(err["code"])
            else:
                error = SensorError(err["msg"])
        return cls(
            data=data,
            fetch_time=state_dict.get("fetch_time"),
            error=error,
            update_count=state_dict.get("update_count", 0),
        )


def display(state: AppState) -> None:
    screen.pen = color.white
    screen.clear()

    # Temperature and humidity display
    temperature = "--.-"
    humidity = "--.-"
    if state.data:
        temperature = f"{state.data.temperature:.1f}"
        humidity = f"{state.data.humidity:.1f}"

    screen.font = rom_font.ignore
    x = 70
    offset_x = 50
    y = 50

    temperature_icon = image.load("thermometer.png")
    screen.blit(temperature_icon, vec2(x, y))

    screen.pen = color.black
    screen.text(f"{temperature} °C", x + offset_x, y)

    y += 50

    humidity_icon = image.load("humidity.png")
    screen.blit(humidity_icon, vec2(x, y))

    screen.pen = color.black
    screen.text(f"{humidity} %", x + offset_x, y)

    # Battery level
    screen.font = rom_font.sins
    battery_text = f"{badge.battery_level()}%"
    (w, _) = screen.measure_text(battery_text)
    screen.text(f"{badge.battery_level()}%", screen.width - w - 5, 5)

    # Last fetch time
    y = 160
    fetch_time_text = "--/-- --:--"
    if state.fetch_time:
        day, month = state.fetch_time[2], state.fetch_time[1]
        hour, minute = state.fetch_time[3], state.fetch_time[4]
        fetch_time_text = f"{day:02d}/{month:02d} {hour:02d}:{minute:02d}"

    screen.font = rom_font.sins
    screen.text(f"{fetch_time_text}", 200, y)

    # Error display
    error_text = ""
    if state.error:
        error_text = state.error.message()

    screen.font = rom_font.sins
    screen.text(f"{error_text}", 5, y)

    badge.mode(state.update_mode())
    badge.update()


def load_state() -> AppState:
    saved = {}
    State.load("mqttooth", saved)
    if saved:
        return AppState.from_dict(saved)
    return AppState()


def update() -> None:
    old_state = load_state()

    result = asyncio.run(fetch_sensor_data())

    new_state = AppState()
    if isinstance(result, SensorData):
        new_state.data = result
        new_state.fetch_time = rtc.datetime()
        new_state.error = None
    else:
        new_state.data = old_state.data
        new_state.fetch_time = old_state.fetch_time
        new_state.error = result
    new_state.update_count = old_state.update_count

    if new_state != old_state or badge.pressed(BUTTON_B):
        display(new_state)
        new_state.update_count += 1
        State.save("mqttooth", new_state.to_dict())

    rtc.set_alarm(minutes=5)

    wait_for_button_or_alarm(timeout=5000)


def on_exit():
    pass


run(update)
