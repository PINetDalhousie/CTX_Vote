#include "contiki.h"
#include "node-id.h"
#include "net/mac/osf/osf.h"
#include "net/mac/osf/osf-packet.h"
#include "net/mac/osf/osf-log.h"
#include "net/mac/osf/osf-stat.h"
#include "net/mac/osf/extensions/osf-ext.h"
#include "os/services/testbed/testbed-rand.h"
#include <stdio.h>
#include<string.h>

#if OSF_CONF_EXT_BV
#include "sys/log.h"
#define LOG_MODULE "BV"
#define LOG_LEVEL LOG_LEVEL_INFO

/* Bit voting for BAD_CRCS */
static uint8_t packet_len;
static uint32_t packet_len_bits;
#define BV_MAX_LEN 2040
static int8_t  bv_arr[BV_MAX_LEN] = {0};
static uint8_t  bv_buf[255] = {0};
static uint8_t  bv_count = 0;
static uint8_t  bv_success;
static uint8_t  bv_ok_cnt, bv_fail_cnt = 0;
static uint16_t bv_crc;
static uint16_t last_id = 0;
static uint8_t  new_id = 1;

/* Error Isolation */
static void create_expected_packet();
static void isolate_errors();
static void update_pkt_payload();
static void print_round_summary();
static void resync(uint16_t, uint16_t);
static uint8_t exp_pkt_buf[255] = {0};
static uint8_t err_arr[BV_MAX_LEN] = {0};
static uint8_t err_flag = 0;
static uint16_t exp_bv_crc;
static uint16_t round_num = 0;
static int bv_success_flag = -1;

/*---------------------------------------------------------------------------*/
static const uint16_t crc16_ccitt_table[256] = {
    0x0000U, 0x1021U, 0x2042U, 0x3063U, 0x4084U, 0x50A5U, 0x60C6U, 0x70E7U,
    0x8108U, 0x9129U, 0xA14AU, 0xB16BU, 0xC18CU, 0xD1ADU, 0xE1CEU, 0xF1EFU,
    0x1231U, 0x0210U, 0x3273U, 0x2252U, 0x52B5U, 0x4294U, 0x72F7U, 0x62D6U,
    0x9339U, 0x8318U, 0xB37BU, 0xA35AU, 0xD3BDU, 0xC39CU, 0xF3FFU, 0xE3DEU,
    0x2462U, 0x3443U, 0x0420U, 0x1401U, 0x64E6U, 0x74C7U, 0x44A4U, 0x5485U,
    0xA56AU, 0xB54BU, 0x8528U, 0x9509U, 0xE5EEU, 0xF5CFU, 0xC5ACU, 0xD58DU,
    0x3653U, 0x2672U, 0x1611U, 0x0630U, 0x76D7U, 0x66F6U, 0x5695U, 0x46B4U,
    0xB75BU, 0xA77AU, 0x9719U, 0x8738U, 0xF7DFU, 0xE7FEU, 0xD79DU, 0xC7BCU,
    0x48C4U, 0x58E5U, 0x6886U, 0x78A7U, 0x0840U, 0x1861U, 0x2802U, 0x3823U,
    0xC9CCU, 0xD9EDU, 0xE98EU, 0xF9AFU, 0x8948U, 0x9969U, 0xA90AU, 0xB92BU,
    0x5AF5U, 0x4AD4U, 0x7AB7U, 0x6A96U, 0x1A71U, 0x0A50U, 0x3A33U, 0x2A12U,
    0xDBFDU, 0xCBDCU, 0xFBBFU, 0xEB9EU, 0x9B79U, 0x8B58U, 0xBB3BU, 0xAB1AU,
    0x6CA6U, 0x7C87U, 0x4CE4U, 0x5CC5U, 0x2C22U, 0x3C03U, 0x0C60U, 0x1C41U,
    0xEDAEU, 0xFD8FU, 0xCDECU, 0xDDCDU, 0xAD2AU, 0xBD0BU, 0x8D68U, 0x9D49U,
    0x7E97U, 0x6EB6U, 0x5ED5U, 0x4EF4U, 0x3E13U, 0x2E32U, 0x1E51U, 0x0E70U,
    0xFF9FU, 0xEFBEU, 0xDFDDU, 0xCFFCU, 0xBF1BU, 0xAF3AU, 0x9F59U, 0x8F78U,
    0x9188U, 0x81A9U, 0xB1CAU, 0xA1EBU, 0xD10CU, 0xC12DU, 0xF14EU, 0xE16FU,
    0x1080U, 0x00A1U, 0x30C2U, 0x20E3U, 0x5004U, 0x4025U, 0x7046U, 0x6067U,
    0x83B9U, 0x9398U, 0xA3FBU, 0xB3DAU, 0xC33DU, 0xD31CU, 0xE37FU, 0xF35EU,
    0x02B1U, 0x1290U, 0x22F3U, 0x32D2U, 0x4235U, 0x5214U, 0x6277U, 0x7256U,
    0xB5EAU, 0xA5CBU, 0x95A8U, 0x8589U, 0xF56EU, 0xE54FU, 0xD52CU, 0xC50DU,
    0x34E2U, 0x24C3U, 0x14A0U, 0x0481U, 0x7466U, 0x6447U, 0x5424U, 0x4405U,
    0xA7DBU, 0xB7FAU, 0x8799U, 0x97B8U, 0xE75FU, 0xF77EU, 0xC71DU, 0xD73CU,
    0x26D3U, 0x36F2U, 0x0691U, 0x16B0U, 0x6657U, 0x7676U, 0x4615U, 0x5634U,
    0xD94CU, 0xC96DU, 0xF90EU, 0xE92FU, 0x99C8U, 0x89E9U, 0xB98AU, 0xA9ABU,
    0x5844U, 0x4865U, 0x7806U, 0x6827U, 0x18C0U, 0x08E1U, 0x3882U, 0x28A3U,
    0xCB7DU, 0xDB5CU, 0xEB3FU, 0xFB1EU, 0x8BF9U, 0x9BD8U, 0xABBBU, 0xBB9AU,
    0x4A75U, 0x5A54U, 0x6A37U, 0x7A16U, 0x0AF1U, 0x1AD0U, 0x2AB3U, 0x3A92U,
    0xFD2EU, 0xED0FU, 0xDD6CU, 0xCD4DU, 0xBDAAU, 0xAD8BU, 0x9DE8U, 0x8DC9U,
    0x7C26U, 0x6C07U, 0x5C64U, 0x4C45U, 0x3CA2U, 0x2C83U, 0x1CE0U, 0x0CC1U,
    0xEF1FU, 0xFF3EU, 0xCF5DU, 0xDF7CU, 0xAF9BU, 0xBFBAU, 0x8FD9U, 0x9FF8U,
    0x6E17U, 0x7E36U, 0x4E55U, 0x5E74U, 0x2E93U, 0x3EB2U, 0x0ED1U, 0x1EF0U
};

/*---------------------------------------------------------------------------*/
static uint16_t
crc16_ccitt(const uint8_t block[], uint32_t blockLength, uint16_t crc)
{
    uint32_t i;
    for(i=0U; i<blockLength; i++){
        uint16_t tmp = (crc >> 8) ^ (uint16_t) block[i];
        crc = ((uint16_t)(crc << 8U)) ^ crc16_ccitt_table[tmp];
    }
    return crc;
}

/*---------------------------------------------------------------------------*/
/* Extension Functions */
/*---------------------------------------------------------------------------*/
static void
start(uint8_t rnd_type, uint8_t initiator, uint8_t data_len)
{
  // Create packet to use for error isolation
  if(tb_node_type == NODE_TYPE_DESTINATION) {
    memset(&exp_pkt_buf, 0, sizeof(exp_pkt_buf));
    create_expected_packet();
    // osf_log_x("Packet Calclatd in start", exp_pkt_buf, osf_buf_len);
  }
  round_num++;  
  if(node_is_synced && new_id) {
    // osf_log_u("new_id", &new_id, 1);
    memset(&bv_arr, 0, sizeof(bv_arr));
    memset(&bv_buf, 0, sizeof(bv_buf));
    bv_count        = 0;
    bv_success      = 0;
    new_id          = 0;
  }
  if(node_is_synced && (rnd_type == OSF_ROUND_S) && initiator) {
    osf_pkt_s_round_t *rnd_pkt = (osf_pkt_s_round_t *)osf_buf_rnd_pkt;
    uint8_t len = OSF_PKT_HDR_LEN + OSF_PKT_RND_LEN(osf.round->type);
    // Ignore the slot relay count (as this changes each timeslot)
    uint8_t slot_tmp = osf_buf_hdr->slot;
    uint16_t ep_tmp = rnd_pkt->epoch;
    osf_buf_hdr->slot = 0;
    rnd_pkt->epoch = 0;
    // Create a crc and add to end of packet
    uint8_t *bv_hdr = &osf_buf[0];
    bv_crc = crc16_ccitt(bv_hdr, len - sizeof(bv_crc), 0xFFFF);
    // osf_log_x("TX", bv_hdr, len);
    memcpy(&rnd_pkt->bv_crc, &bv_crc, sizeof(bv_crc));
    // osf_log_x("CRC", &rnd_pkt->bv_crc, 2);
    // Put the slot relay count back in
    osf_buf_hdr->slot = slot_tmp;
    rnd_pkt->epoch = ep_tmp;
    last_id = rnd_pkt->id;
  }
}

/*---------------------------------------------------------------------------*/
static void
rx_ok(uint8_t rnd_type, uint8_t *data, uint8_t data_len)
{
  osf_pkt_s_round_t *rnd_pkt = (osf_pkt_s_round_t *)osf_buf_rnd_pkt;
  if (osf.proto->role == OSF_ROLE_DST) {
  if(node_is_synced && (rnd_type == OSF_ROUND_S) && rnd_pkt->id != last_id) {
    last_id = rnd_pkt->id;
    new_id = 1;
    // osf_log_u("nid", &last_id, 2);
  }
  
  osf_pkt_hdr_t *exp_hdr = (osf_pkt_hdr_t *)&exp_pkt_buf[0];
  exp_hdr->slot = osf.slot;

  if (was_out_of_sync == 1 && pkt_flag == 1) {
    uint16_t tmp = (osf.epoch-1) % 3;
    tmp = (osf.epoch-1) - tmp;
    resync(rnd_pkt->id, tmp);

    // tb_exp_id = rnd_pkt->id;
    was_out_of_sync = 0;
  }
  // osf_log_x("Packet Calclatd in rx_ok", exp_pkt_buf, osf_buf_len);
  // osf_log_x("Packet Received in rx_ok", osf_buf, osf_buf_len);
  }
}

/*---------------------------------------------------------------------------*/
static void
rx_error()
{
  // Try bit voting if we haven't already been successful. We can then use
  // the packet at the END of the flood (we might still get a correct pkt)
  if ((osf.proto->role == OSF_ROLE_DST)){
    if(node_is_synced && !bv_success) {
      uint32_t i;
      packet_len = osf_buf_len;
      packet_len_bits = packet_len * 8;

      bv_count++;
      memcpy(bv_buf, osf_buf, packet_len);
      // osf_pkt_hdr_t *bv_hdr = (osf_pkt_hdr_t *)&bv_buf[OSF_PKT_PHY_LEN(osf.rconf->phy->mode)];
      osf_pkt_hdr_t *bv_hdr = (osf_pkt_hdr_t *)&bv_buf[0];
      osf_pkt_s_round_t *bv_pkt = (osf_pkt_s_round_t *)&bv_buf[OSF_PKT_HDR_LEN];
      // bv_buf[0] &= ~(osf_buf_hdr->slot); // if we have a mask
      uint8_t slot_tmp = bv_hdr->slot;
      uint16_t ep_tmp = bv_pkt->epoch;
      bv_hdr->slot = 0;
      bv_pkt->epoch = 0;
      // osf_log_x("ERR", &bv_buf, packet_len);
      for (i = 0; i < packet_len_bits; i++) {
        if(OSF_CHK_BIT_BYTE(bv_buf, i)) {
          bv_arr[i]++;
        } else {
          bv_arr[i]--;
        }
      }
      bv_hdr->slot = slot_tmp;
      bv_pkt->epoch = ep_tmp;
    }
    // Make sure slot is updated then perform error isolation
    osf_pkt_hdr_t *exp_hdr = (osf_pkt_hdr_t *)&exp_pkt_buf[0];
    exp_hdr->slot = osf.slot;

    // osf_log_x("Packet Calclatd in rx_er", exp_pkt_buf, osf_buf_len);
    // osf_log_x("Packet Received in rx_er", osf_buf, osf_buf_len);

    // only perform error isolation if we know the generated packet is correct
    if (was_out_of_sync == 0) {
      isolate_errors();
      err_flag = 1;
    }
  }
}

/*---------------------------------------------------------------------------*/
static void
stop()
{
  if (node_is_synced && osf.proto->role == OSF_ROLE_DST) {
    if(!osf.n_rx_ok && bv_count > 2) {
      uint32_t i;
      memset(&bv_buf, 0, sizeof(bv_buf));
      // convert bv_arr to ones and zeros
      // packet_len_bits = (osf_buf_len + sizeof(bv_crc)) * 8;
      packet_len_bits = (osf_buf_len) * 8;
      for (i = 0; i < packet_len_bits; i++) {
        if((bv_arr[i] >= 0) ? 1 : 0) {
          OSF_SET_BIT_BYTE(bv_buf, i);
        } else {
          OSF_CLR_BIT_BYTE(bv_buf, i);
        }
      }
      // osf_pkt_hdr_t *bv_hdr = (osf_pkt_hdr_t *)&bv_buf[OSF_PKT_PHY_LEN(osf.rconf->phy->mode)];
      osf_pkt_hdr_t *bv_hdr = (osf_pkt_hdr_t *)&bv_buf[0];
      osf_pkt_s_round_t *bv_pkt = (osf_pkt_s_round_t *)&bv_buf[OSF_PKT_HDR_LEN];
      // Ignore the slot relay count (as this changes each timeslot)
      uint8_t slot_tmp = bv_hdr->slot;
      uint16_t ep_tmp = bv_pkt->epoch;
      bv_hdr->slot = 0;
      bv_pkt->epoch = 0;
      bv_crc = crc16_ccitt(&bv_buf[0], packet_len - sizeof(bv_crc), 0xFFFF);
      // osf_log_x("PKT", &bv_buf, packet_len);
      bv_hdr->slot = slot_tmp;
      bv_pkt->epoch = ep_tmp;
      // osf_log_x("EXP", &bv_crc, 2);
      // Check to see if the packet id is new. Even this is due to corruption,
      // we can't be sure that this isn't actually a new packet, so next flood
      // we will reset the bit voting.
      // osf_log_x("RCV",&bv_pkt->bv_crc, 2);
      // osf_log_x("rid",&bv_pkt->id, 2);
      // osf_log_x("lid",&last_id, 2);
      if(bv_crc == (*(uint16_t *)(&bv_buf[packet_len - sizeof(bv_crc)]))) {
        bv_success = 1;
        bv_ok_cnt++;
        bv_success_flag = 1;

        if (was_out_of_sync == 1 && pkt_flag == 1) {
          uint16_t tmp = (osf.epoch-1) % 3;
          tmp = (osf.epoch-1) - tmp;
          resync(bv_pkt->id, tmp);
          
          // tb_exp_id = bv_pkt->id;
          was_out_of_sync = 0;
        }
        // osf_log_x("PKT", &bv_buf, packet_len);
        // osf_log_u("OK!", &bv_ok_cnt, 1);
        // osf_log_u("BV_COUNT", &bv_count, 1);
        // copy the application data from the bv stack
        if(bv_pkt->id != last_id) {
          last_id = bv_pkt->id;
          new_id = 1;
          // osf_log_u("nid", &last_id, 2);
        }
        osf.n_rx_ok++;
        memcpy(osf_buf, &bv_buf, packet_len);
      } else {
        bv_fail_cnt++;
        bv_success_flag = 0;
        // osf_log_u("FAIL!", &bv_fail_cnt, 1);
        // osf_log_u("BV_COUNT", &bv_count, 1);
      }
      // osf_log_d("bits", &bv_arr, packet_len_bits);
    }

  if(tb_node_type == NODE_TYPE_DESTINATION) {
    print_round_summary();
  }
  // clear errors for next round
  memset(&err_arr, 0, sizeof(err_arr));
  bv_success_flag = -1;
  err_flag = 0;
  }

}

/*---------------------------------------------------------------------------*/
/* Error Isolation 
   Little-endian packets. */
/*---------------------------------------------------------------------------*/
static void
isolate_errors()
{
  packet_len_bits = osf_buf_len * 8;
  uint32_t i;
  for (i = 8; i < packet_len_bits; i++) {
    if(OSF_CHK_BIT_BYTE(exp_pkt_buf, i) ^ OSF_CHK_BIT_BYTE(osf_buf, i)) {
      err_arr[i]++;
    }
  }
}

/*---------------------------------------------------------------------------*/
static void
create_expected_packet()
{
  packet_len = osf_buf_len;
  
  osf_pkt_hdr_t *exp_hdr = (osf_pkt_hdr_t *)&exp_pkt_buf[0];
  osf_pkt_s_round_t *exp_pkt = (osf_pkt_s_round_t *)&exp_pkt_buf[OSF_PKT_HDR_LEN];
  exp_hdr->src = osf.sources[0];        // known source
  if (!pkt_flag) {
    exp_hdr->dst = 0xff;                // known dst
    exp_pkt->id = 0;
  }
  else {
    exp_hdr->dst = node_id; // known dst
    update_pkt_payload(&exp_pkt->payload[0]);
    exp_pkt->id = tb_exp_id;
  }
  exp_hdr->slot = 0;                    // 0 slot for bv_crc
  exp_pkt->epoch = 0;                   // 0 epoch for bv_crc

  // Find & add bv_crc
  exp_bv_crc = crc16_ccitt(&exp_pkt_buf[0], packet_len - sizeof(exp_bv_crc), 0xFFFF);
  memcpy(exp_pkt->bv_crc, &exp_bv_crc, sizeof(exp_bv_crc));

  exp_hdr->slot = osf.slot;             // current slot
  exp_pkt->epoch = osf.epoch;           // current epoch
}

/*---------------------------------------------------------------------------*/
static void
update_pkt_payload(uint8_t *dst_buf){
  uint8_t i;
  for(i = 0; i < tb_msg_len; i++) {
    dst_buf[i] = exp_buf[i];
  }
}

/*---------------------------------------------------------------------------*/
static void
resync(uint16_t id, uint16_t seed) {
  tb_exp_id = id;
  tb_rand_init(seed);

  // update buffer
  uint8_t i;
  for(i = 0; i < tb_msg_len; i++)
  {
    TB_RAND(exp_buf[i], TB_RAND_BUF_MAX);
  }
}

/*---------------------------------------------------------------------------*/
static void
print_round_summary()
{
  packet_len_bits = osf_buf_len*8;

  PRINT("EP:%d,RND:%d,N_RX:%d,N_ERR_PKTS:%d,"
        "BV_CNT:%d,BV_SCS_FLAG:%d,ERRS:{",
        osf.epoch, round_num, osf.n_rx_ok + osf.n_rx_crc, osf.n_rx_crc,
        bv_count, bv_success_flag);
  
  if (err_flag){
    uint32_t i;
    for(i = 0; i < packet_len_bits; i++) {
      if(err_arr[i] != 0) {
        PRINT("%ld:%d;", i, err_arr[i]);
      }
    }
  }
  PRINT("},SLTS:");
}

/*---------------------------------------------------------------------------*/
/* BV extension driver */
/*---------------------------------------------------------------------------*/
osf_ext_d_t osf_ext_d_bv = {
    "osf_bv",
    NULL,
    NULL,
    &start,
    NULL,
    NULL,
    &rx_ok,
    &rx_error,
    &stop,
};
#endif