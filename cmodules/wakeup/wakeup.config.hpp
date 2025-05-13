#include "hardware/i2c.h"

#ifndef WAKEUP_VSYS_EN
#define WAKEUP_VSYS_EN 10
#endif

#ifndef WAKEUP_LED
#define WAKEUP_LED 8
#endif

// Pins to toggle on wakeup
#ifndef WAKEUP_PIN_MASK
#define WAKEUP_PIN_MASK ((0b1 << WAKEUP_VSYS_EN) | (0b1 << WAKEUP_LED))
#endif

// Direction
#ifndef WAKEUP_PIN_DIR
#define WAKEUP_PIN_DIR ((0b1 << WAKEUP_VSYS_EN) | (0b1 << WAKEUP_LED))
#endif

// Value
#ifndef WAKEUP_PIN_VALUE
#define WAKEUP_PIN_VALUE ((0b1 << WAKEUP_VSYS_EN) | (0b1 << WAKEUP_LED))
#endif

#ifndef WAKEUP_HAS_RTC
#define WAKEUP_HAS_RTC (0)
#endif

#ifndef WAKEUP_RTC_SDA
#define WAKEUP_RTC_SDA (4)
#endif

#ifndef WAKEUP_RTC_SCL
#define WAKEUP_RTC_SCL (5)
#endif

#ifndef WAKEUP_RTC_I2C_ADDR
#define WAKEUP_RTC_I2C_ADDR 0x51
#endif

#ifndef WAKEUP_RTC_I2C_INST
#define WAKEUP_RTC_I2C_INST i2c0
#endif
