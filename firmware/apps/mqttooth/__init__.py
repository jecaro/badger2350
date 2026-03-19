import aioble
import asyncio
import bluetooth
import os
import struct
import sys


sys.path.insert(0, "/system/apps/mqttooth")
os.chdir("/system/apps/mqttooth")


# Type alias for rtc.datetime() return value: (year, month, day, hour, minute,
# second, dow)
DateTime = tuple
# Type alias for history entries: (DateTime, SensorData | SensorError |
# GattError)
HistoryPoint = tuple
# Type alias for graph data points: (DateTime, float)
DataPoint = tuple


# Graph UI constants and functions

SCREEN_WIDTH = 264
SCREEN_HEIGHT = 176

STATUS_BAR_HEIGHT = 16
USABLE_HEIGHT = SCREEN_HEIGHT - STATUS_BAR_HEIGHT
HALF_HEIGHT = USABLE_HEIGHT // 2

GRAPH_LEFT_MARGIN = 10
GRAPH_RIGHT_MARGIN = 25
GRAPH_TOP_MARGIN = 5
GRAPH_BOTTOM_MARGIN = 18

GRAPH_WIDTH = SCREEN_WIDTH - GRAPH_LEFT_MARGIN - GRAPH_RIGHT_MARGIN
GRAPH_HEIGHT = HALF_HEIGHT - GRAPH_TOP_MARGIN - GRAPH_BOTTOM_MARGIN


def _thick_line(x1: int, y1: int, x2: int, y2: int, thickness: int = 2) -> None:
    """Draw a thicker line by drawing multiple parallel lines."""
    screen.line(x1, y1, x2, y2)
    for i in range(1, thickness):
        offset = i // 2 + 1
        if i % 2 == 0:
            offset = -offset
        # Offset perpendicular to the line
        if abs(x2 - x1) > abs(y2 - y1):
            # More horizontal - offset vertically
            screen.line(x1, y1 + offset, x2, y2 + offset)
        else:
            # More vertical - offset horizontally
            screen.line(x1 + offset, y1, x2 + offset, y2)


# 19 hours
HISTORY_WINDOW_SECS = 19 * 60 * 60


def filter_visible_points(
    data_points: list[HistoryPoint], current_time: DateTime | None
) -> list[HistoryPoint]:
    """Filter data points to only those within the visible time window."""
    if not data_points or not current_time:
        return data_points

    end_secs = datetime_to_secs(current_time)
    start_secs = end_secs - HISTORY_WINDOW_SECS

    visible = []
    for dt, value in data_points:
        point_secs = datetime_to_secs(dt)
        if start_secs <= point_secs <= end_secs:
            visible.append((dt, value))
    return visible


def draw_graph(
    data_points: list[DataPoint],
    current_time: DateTime | None,
    y_offset: int,
    y_min: int,
    y_max: int,
) -> None:
    """Draw a graph with axes, ticks, and data points."""
    graph_x = GRAPH_LEFT_MARGIN
    graph_y = y_offset + GRAPH_TOP_MARGIN
    graph_w = GRAPH_WIDTH
    graph_h = GRAPH_HEIGHT

    screen.pen = color.black

    # Draw axes
    _thick_line(
        graph_x + graph_w, graph_y, graph_x + graph_w, graph_y + graph_h
    )  # Y-axis on right
    _thick_line(graph_x, graph_y + graph_h, graph_x + graph_w, graph_y + graph_h)

    # Draw Y-axis ticks and labels (on right side)
    screen.font = rom_font.teatime
    y_range = y_max - y_min
    y_ticks = compute_y_ticks(y_min, y_max)

    for y_val in y_ticks:
        y_ratio = (y_val - y_min) / y_range if y_range > 0 else 0
        tick_y = graph_y + graph_h - int(y_ratio * graph_h)
        # Tick mark
        screen.line(graph_x + graph_w, tick_y, graph_x + graph_w + 3, tick_y)
        # Label
        screen.text(f"{y_val}", graph_x + graph_w + 5, tick_y - 6)

    # Fixed time window
    end_secs = datetime_to_secs(current_time)
    start_secs = end_secs - HISTORY_WINDOW_SECS

    # Draw X-axis ticks and time labels (every 3 hours: 0, 3, 6, 9, ...)
    # Find first 3-hour mark at or after start_secs
    first_tick = ((start_secs // (3 * 3600)) + 1) * (3 * 3600)
    for tick_secs in range(first_tick, end_secs + 1, 3 * 3600):
        x_ratio = (tick_secs - start_secs) / HISTORY_WINDOW_SECS
        tick_x = graph_x + int(x_ratio * graph_w)

        screen.line(tick_x, graph_y + graph_h, tick_x, graph_y + graph_h + 3)

        tick_hour = (tick_secs // 3600) % 24
        time_label = f"{tick_hour}"
        label_w, _ = screen.measure_text(time_label)
        screen.text(time_label, tick_x - label_w // 2, graph_y + graph_h + 4)

    # Draw data line
    if data_points and len(data_points) > 1:
        prev_x, prev_y = None, None

        for dt, value in data_points:
            point_secs = datetime_to_secs(dt)
            x_ratio = (point_secs - start_secs) / HISTORY_WINDOW_SECS
            px = graph_x + int(x_ratio * graph_w)

            # Skip points outside visible window
            if x_ratio < 0 or x_ratio > 1:
                prev_x, prev_y = None, None
                continue

            y_ratio = (value - y_min) / y_range if y_range > 0 else 0.5
            y_ratio = max(0, min(1, y_ratio))
            py = graph_y + graph_h - int(y_ratio * graph_h)

            if prev_x is not None:
                # Skip lines that would draw over the icon/value area (top-left)
                prev_in_zone = prev_x < 120 and prev_y < y_offset + 40
                curr_in_zone = px < 120 and py < y_offset + 40
                if not prev_in_zone and not curr_in_zone:
                    _thick_line(prev_x, prev_y, px, py)

            prev_x, prev_y = px, py


def draw_current_value(icon, value: float | None, unit: str, y_offset: int) -> None:
    """Draw the icon and current value in the top-left of a graph section."""
    # Uncomment to debug exclusion zone boundary
    # screen.pen = color.black
    # screen.line(0, y_offset + 40, 120, y_offset + 40)  # horizontal
    # screen.line(120, y_offset, 120, y_offset + 40)  # vertical

    icon_x = 5
    icon_y = y_offset + 5

    screen.blit(icon, vec2(icon_x, icon_y))

    screen.font = rom_font.ignore
    screen.pen = color.black

    if value is not None:
        value_text = f"{value:.1f}"
    else:
        value_text = "--.-"

    value_x = icon_x + 35
    value_y = y_offset + 5
    screen.text(f"{value_text} {unit}", value_x, value_y)


def draw_status_bar(
    battery_level: int, fetch_time: DateTime | None, error_message: str | None
) -> None:
    """Draw the status bar at the bottom of the screen."""
    y = USABLE_HEIGHT + 2

    screen.font = rom_font.sins
    screen.pen = color.black

    if error_message:
        screen.text(error_message, 5, y)

    if fetch_time:
        day = fetch_time[2]
        month = fetch_time[1]
        hour = fetch_time[3]
        minute = fetch_time[4]
        time_text = f"{day:02d}/{month:02d} {hour:02d}:{minute:02d}"
    else:
        time_text = "--/-- --:--"

    time_w, _ = screen.measure_text(time_text)
    screen.text(time_text, (SCREEN_WIDTH - time_w) // 2, y)

    battery_text = f"{battery_level}%"
    batt_w, _ = screen.measure_text(battery_text)
    screen.text(battery_text, SCREEN_WIDTH - batt_w - 5, y)


# App logic


class SensorError:
    def __init__(self, msg: str):
        self.msg = msg

    def __eq__(self, other: object) -> bool:
        return isinstance(other, SensorError) and self.msg == other.msg

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


def datetime_to_secs(datetime: DateTime) -> int:
    """Convert datetime tuple to absolute seconds (since year 0, approximately)."""
    year = datetime[0]
    month = datetime[1]
    day = datetime[2]
    hour = datetime[3]
    minute = datetime[4]
    second = datetime[5]
    # Simple approximation: assume 365 days/year, 30 days/month
    return (((year * 365 + month * 30 + day) * 24 + hour) * 60 + minute) * 60 + second


class AppState:
    """Application state for the mqttooth app.

    State is composed of:
    - history: recorded and stored after every fetch, regardless of whether the
      display is refreshed. Used to draw graphs and derive the last successful
      sensor data.
    - last_displayed: the fetch result that triggered the last display refresh.
      This may differ from the latest value in history because the display is
      only refreshed when the new result differs significantly from what is
      currently shown (e.g. temperature changes beyond a threshold).
    - update_count: tracks number of display refreshes for full/partial update
      cycling.

    The values shown on screen (current temperature, humidity, fetch time) are
    derived from history by finding the most recent successful SensorData entry.
    """

    FULL_UPDATE_INTERVAL = 10

    def __init__(
        self,
        update_count: int = 0,
        history: list[HistoryPoint] | None = None,
        last_displayed: SensorData | SensorError | GattError | None = None,
        page: int = 0,
    ):
        self.update_count = update_count
        self.history = history if history is not None else []
        self.last_displayed = last_displayed
        self.page = page

    def get_last_data(self) -> SensorData | None:
        """Latest successful sensor data."""
        for _, result in reversed(self.history):
            if isinstance(result, SensorData):
                return result
        return None

    def get_last_fetch_time(self) -> DateTime | None:
        """Time of latest successful fetch."""
        for dt, result in reversed(self.history):
            if isinstance(result, SensorData):
                return dt
        return None

    def get_last_error(self) -> SensorError | GattError | None:
        """Error if the last fetch failed, None otherwise."""
        if self.history:
            _, result = self.history[-1]
            if not isinstance(result, SensorData):
                return result
        return None

    def update_mode(self) -> int:
        if self.update_count % self.FULL_UPDATE_INTERVAL == 0:
            return FULL_UPDATE
        return MEDIUM_UPDATE

    def add_history_point(
        self,
        datetime: DateTime,
        result: SensorData | SensorError | GattError,
    ) -> None:
        """Add a new history point and trim old ones by time window."""
        self.history.append((datetime, result))

        # Trim points outside the time window
        curr_secs = datetime_to_secs(datetime)
        self.history = [
            (t, r)
            for t, r in self.history
            if curr_secs - datetime_to_secs(t) <= HISTORY_WINDOW_SECS
        ]

    @staticmethod
    def _serialize_result(result: SensorData | SensorError | GattError) -> dict:
        if isinstance(result, SensorData):
            return {
                "type": "SensorData",
                "temperature": result.temperature,
                "humidity": result.humidity,
            }

        if isinstance(result, GattError):
            return {"type": "GattError", "code": result.code}

        return {"type": "SensorError", "msg": result.msg}

    @staticmethod
    def _deserialize_result(d: dict) -> SensorData | SensorError | GattError:
        if d["type"] == "SensorData":
            return SensorData(d["temperature"], d["humidity"])

        if d["type"] == "GattError":
            return GattError(d["code"])

        return SensorError(d["msg"])

    def to_dict(self) -> dict:
        history = [(dt, self._serialize_result(result)) for dt, result in self.history]

        return {
            "update_count": self.update_count,
            "history": history,
            "last_displayed": self._serialize_result(self.last_displayed)
            if self.last_displayed
            else None,
            "page": self.page,
        }

    @classmethod
    def from_dict(cls, state_dict: dict) -> "AppState":
        history = []
        for dt, result_dict in state_dict.get("history", []):
            history.append((tuple(dt), cls._deserialize_result(result_dict)))

        last_displayed_dict = state_dict.get("last_displayed")
        last_displayed = (
            cls._deserialize_result(last_displayed_dict)
            if last_displayed_dict
            else None
        )

        return cls(
            update_count=state_dict.get("update_count", 0),
            history=history,
            last_displayed=last_displayed,
            page=state_dict.get("page", 0),
        )

    @classmethod
    def load(cls) -> "AppState":
        saved = {}
        State.load("mqttooth", saved)
        if saved:
            return cls.from_dict(saved)
        return cls()

    def save(self) -> None:
        State.save("mqttooth", self.to_dict())


def compute_y_range(points: list[DataPoint]) -> tuple[int, int]:
    """Compute y-axis range from full min-max of all points."""
    import math

    values = [value for _, value in points]
    y_min = math.floor(min(values))
    y_max = math.ceil(max(values))

    # Ensure minimum range of 1
    if y_max == y_min:
        y_max = y_min + 1

    return y_min, y_max


def compute_y_ticks(y_min: int, y_max: int) -> list[int]:
    """Compute tick positions as integers, with at most MAX_Y_TICKS ticks.

    Always includes y_min and y_max, with evenly-spaced interior ticks.
    """
    MAX_Y_TICKS = 7
    # Find smallest step that gives <= MAX_Y_TICKS - 2 interior ticks
    for step in (1, 2, 3, 4, 5, 10, 20, 25, 30, 40, 50):
        # Interior ticks: multiples of step strictly between y_min and y_max
        first_interior = ((y_min // step) + 1) * step
        last_interior = (y_max // step) * step
        if last_interior == y_max:
            last_interior -= step

        if first_interior > last_interior:
            num_interior = 0
        else:
            num_interior = (last_interior - first_interior) // step + 1

        # Total ticks = min + interior + max
        if num_interior + 2 <= MAX_Y_TICKS:
            ticks = [y_min]
            ticks.extend(range(first_interior, last_interior + 1, step))
            ticks.append(y_max)
            return ticks

    # Fallback on just min and max
    return [y_min, y_max]


def display_simple(state: AppState) -> None:
    screen.pen = color.white
    screen.clear()

    data = state.get_last_data()
    temperature = f"{data.temperature:.1f}" if data else "--.-"
    humidity = f"{data.humidity:.1f}" if data else "--.-"

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

    error = state.get_last_error()
    error_message = error.message() if error else None
    draw_status_bar(badge.battery_level(), state.get_last_fetch_time(), error_message)

    badge.mode(state.update_mode())
    badge.update()


def display_charts(state: AppState) -> None:
    screen.pen = color.white
    screen.clear()

    # Extract current values
    data = state.get_last_data()
    current_temperature = data.temperature if data else None
    current_humidity = data.humidity if data else None

    # Filter to visible points and extract (dt, value) lists
    fetch_time = state.get_last_fetch_time()
    visible = filter_visible_points(state.history, fetch_time)

    temperature_points = [
        (dt, r.temperature) for dt, r in visible if isinstance(r, SensorData)
    ]
    humidity_points = [
        (dt, r.humidity) for dt, r in visible if isinstance(r, SensorData)
    ]

    if temperature_points:
        temperature_min, temperature_max = compute_y_range(temperature_points)
    elif current_temperature is not None:
        temperature_min = int(current_temperature)
        temperature_max = temperature_min + 1
    else:
        temperature_min, temperature_max = 15, 25

    if humidity_points:
        humidity_min, humidity_max = compute_y_range(humidity_points)
    elif current_humidity is not None:
        humidity_min = int(current_humidity)
        humidity_max = humidity_min + 1
    else:
        humidity_min, humidity_max = 50, 60

    # Draw temperature section (top half)
    temperature_icon = image.load("thermometer.png")
    draw_current_value(temperature_icon, current_temperature, "°C", 0)
    draw_graph(temperature_points, fetch_time, 0, temperature_min, temperature_max)

    # Draw humidity section (bottom half)
    humidity_icon = image.load("humidity.png")
    draw_current_value(humidity_icon, current_humidity, "%", HALF_HEIGHT)
    draw_graph(humidity_points, fetch_time, HALF_HEIGHT, humidity_min, humidity_max)

    # Draw status bar
    error = state.get_last_error()
    error_message = error.message() if error else None
    draw_status_bar(badge.battery_level(), fetch_time, error_message)

    badge.mode(state.update_mode())
    badge.update()


PAGE_COUNT = 2


def display(state: AppState) -> None:
    if state.page == 0:
        display_simple(state)
    elif state.page == 1:
        display_charts(state)
    state.update_count += 1


def update() -> None:
    state = AppState.load()

    if badge.pressed(BUTTON_UP):
        state.page = (state.page - 1) % PAGE_COUNT
        display(state)
    elif badge.pressed(BUTTON_DOWN):
        state.page = (state.page + 1) % PAGE_COUNT
        display(state)

    else:
        result = asyncio.run(fetch_sensor_data())

        now = rtc.datetime()
        state.add_history_point(now, result)

        if result != state.last_displayed or badge.pressed(BUTTON_B):
            display(state)
            state.last_displayed = result

    state.save()
    rtc.set_alarm(minutes=5)
    wait_for_button_or_alarm(timeout=5000)


def on_exit() -> None:
    pass


run(update)
