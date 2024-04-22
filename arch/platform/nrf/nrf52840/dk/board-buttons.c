/*
 * Copyright (C) 2020 Yago Fontoura do Rosario <yago.rosario@hotmail.com.br>
 * All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions
 * are met:
 * 1. Redistributions of source code must retain the above copyright
 *    notice, this list of conditions and the following disclaimer.
 * 2. Redistributions in binary form must reproduce the above copyright
 *    notice, this list of conditions and the following disclaimer in the
 *    documentation and/or other materials provided with the distribution.
 * 3. Neither the name of the copyright holder nor the names of its
 *    contributors may be used to endorse or promote products derived
 *    from this software without specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
 * ``AS IS'' AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
 * LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
 * FOR A PARTICULAR PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL THE
 * COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
 * INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
 * (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
 * SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
 * HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,
 * STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
 * ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED
 * OF THE POSSIBILITY OF SUCH DAMAGE.
 */
/*---------------------------------------------------------------------------*/
/**
 * \addtogroup nrf-platforms
 * @{
 *
 * \addtogroup nrf52840-dk
 * @{
 *
 * \file
 *         nRF52840 DK specific buttons driver implementation.
 * \author
 *         Yago Fontoura do Rosario <yago.rosario@hotmail.com.br>
 */
/*---------------------------------------------------------------------------*/
#include "contiki.h"
#include "dev/button-hal.h"
/*---------------------------------------------------------------------------*/
BUTTON_HAL_BUTTON(btn_1, "Button 1", NRF_BUTTON1_PORT, NRF_BUTTON1_PIN, \
                  GPIO_HAL_PIN_CFG_PULL_UP, BUTTON_HAL_ID_BUTTON_ZERO, true);
BUTTON_HAL_BUTTON(btn_2, "Button 2", NRF_BUTTON2_PORT, NRF_BUTTON2_PIN, \
                  GPIO_HAL_PIN_CFG_PULL_UP, BUTTON_HAL_ID_BUTTON_ONE, true);
BUTTON_HAL_BUTTON(btn_3, "Button 3", NRF_BUTTON3_PORT, NRF_BUTTON3_PIN, \
                  GPIO_HAL_PIN_CFG_PULL_UP, BUTTON_HAL_ID_BUTTON_TWO, true);
BUTTON_HAL_BUTTON(btn_4, "Button 4", NRF_BUTTON4_PORT, NRF_BUTTON4_PIN, \
                  GPIO_HAL_PIN_CFG_PULL_UP, BUTTON_HAL_ID_BUTTON_THREE, true);
/*---------------------------------------------------------------------------*/
BUTTON_HAL_BUTTONS(&btn_1, &btn_2, &btn_3, &btn_4);
/*---------------------------------------------------------------------------*/
/** 
 * @} 
 * @} 
 */
