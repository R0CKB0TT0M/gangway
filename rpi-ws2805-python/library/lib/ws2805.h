/*
 * ws2805.h
 *
 * Copyright (c) 2014 Jeremy Garff <jer @ jers.net>
 *
 * All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without modification, are permitted
 * provided that the following conditions are met:
 *
 *     1.  Redistributions of source code must retain the above copyright notice, this list of
 *         conditions and the following disclaimer.
 *     2.  Redistributions in binary form must reproduce the above copyright notice, this list
 *         of conditions and the following disclaimer in the documentation and/or other materials
 *         provided with the distribution.
 *     3.  Neither the name of the owner nor the names of its contributors may be used to endorse
 *         or promote products derived from this software without specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR
 * IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND
 * FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER BE
 * LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
 * (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA,
 * OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
 * CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
 * OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 *
 */


#ifndef __ws2805_H__
#define __ws2805_H__

#ifdef __cplusplus
extern "C" {
#endif

#include <stdint.h>

#include "rpihw.h"
#include "pwm.h"


#define ws2805_TARGET_FREQ                       800000   // Can go as low as 400000

// 4 color R, G, B and W ordering
#define SK6812_STRIP_RGBW                        0x18100800
#define SK6812_STRIP_RBGW                        0x18100008
#define SK6812_STRIP_GRBW                        0x18081000
#define SK6812_STRIP_GBRW                        0x18080010
#define SK6812_STRIP_BRGW                        0x18001008
#define SK6812_STRIP_BGRW                        0x18000810
#define SK6812_SHIFT_WMASK                       0xf0000000

// 3 color R, G and B ordering
#define ws2805_STRIP_RGB                         0x00100800
#define ws2805_STRIP_RBG                         0x00100008
#define ws2805_STRIP_GRB                         0x00081000
#define ws2805_STRIP_GBR                         0x00080010
#define ws2805_STRIP_BRG                         0x00001008
#define ws2805_STRIP_BGR                         0x00000810

// predefined fixed LED types
#define WS2812_STRIP                             ws2805_STRIP_GRB
#define SK6812_STRIP                             ws2805_STRIP_GRB
#define SK6812W_STRIP                            SK6812_STRIP_GRBW

struct ws2805_device;

typedef uint64_t ws2805_led_t;                   //< 0xXXWWCCBBRRGGBB
typedef struct ws2805_channel_t
{
    int gpionum;                                 //< GPIO Pin with PWM alternate function, 0 if unused
    int invert;                                  //< Invert output signal
    int count;                                   //< Number of LEDs, 0 if channel is unused
    int strip_type;                              //< Strip color layout -- one of ws2805_STRIP_xxx constants
    ws2805_led_t *leds;                          //< LED buffers, allocated by driver based on count
    uint8_t brightness;                          //< Brightness value between 0 and 255
    uint8_t wshift;                              //< White shift value
    uint8_t rshift;                              //< Red shift value
    uint8_t gshift;                              //< Green shift value
    uint8_t bshift;                              //< Blue shift value
    uint8_t *gamma;                              //< Gamma correction table
} ws2805_channel_t;

typedef struct ws2805_t
{
    uint64_t render_wait_time;                   //< time in µs before the next render can run
    struct ws2805_device *device;                //< Private data for driver use
    const rpi_hw_t *rpi_hw;                      //< RPI Hardware Information
    uint32_t freq;                               //< Required output frequency
    int dmanum;                                  //< DMA number _not_ already in use
    ws2805_channel_t channel[RPI_PWM_CHANNELS];
} ws2805_t;

#define ws2805_RETURN_STATES(X)                                                             \
            X(0, ws2805_SUCCESS, "Success"),                                                \
            X(-1, ws2805_ERROR_GENERIC, "Generic failure"),                                 \
            X(-2, ws2805_ERROR_OUT_OF_MEMORY, "Out of memory"),                             \
            X(-3, ws2805_ERROR_HW_NOT_SUPPORTED, "Hardware revision is not supported"),     \
            X(-4, ws2805_ERROR_MEM_LOCK, "Memory lock failed"),                             \
            X(-5, ws2805_ERROR_MMAP, "mmap() failed"),                                      \
            X(-6, ws2805_ERROR_MAP_REGISTERS, "Unable to map registers into userspace"),    \
            X(-7, ws2805_ERROR_GPIO_INIT, "Unable to initialize GPIO"),                     \
            X(-8, ws2805_ERROR_PWM_SETUP, "Unable to initialize PWM"),                      \
            X(-9, ws2805_ERROR_MAILBOX_DEVICE, "Failed to create mailbox device"),          \
            X(-10, ws2805_ERROR_DMA, "DMA error"),                                          \
            X(-11, ws2805_ERROR_ILLEGAL_GPIO, "Selected GPIO not possible"),                \
            X(-12, ws2805_ERROR_PCM_SETUP, "Unable to initialize PCM"),                     \
            X(-13, ws2805_ERROR_SPI_SETUP, "Unable to initialize SPI"),                     \
            X(-14, ws2805_ERROR_SPI_TRANSFER, "SPI transfer error")                         \

#define ws2805_RETURN_STATES_ENUM(state, name, str) name = state
#define ws2805_RETURN_STATES_STRING(state, name, str) str

typedef enum {
    ws2805_RETURN_STATES(ws2805_RETURN_STATES_ENUM),

    ws2805_RETURN_STATE_COUNT
} ws2805_return_t;

ws2805_return_t ws2805_init(ws2805_t *ws2805);                                  //< Initialize buffers/hardware
void ws2805_fini(ws2805_t *ws2805);                                             //< Tear it all down
ws2805_return_t ws2805_render(ws2805_t *ws2805);                                //< Send LEDs off to hardware
ws2805_return_t ws2805_wait(ws2805_t *ws2805);                                  //< Wait for DMA completion
const char * ws2805_get_return_t_str(const ws2805_return_t state);              //< Get string representation of the given return state
void ws2805_set_custom_gamma_factor(ws2805_t *ws2805, double gamma_factor);     //< Set a custom Gamma correction array based on a gamma correction factor

#ifdef __cplusplus
}
#endif

#endif /* __ws2805_H__ */
