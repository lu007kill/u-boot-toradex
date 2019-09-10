/* SPDX-License-Identifier: GPL-2.0+ */
/*
 * Copyright 2018-2019 Toradex
 */

#ifndef __APALIS_IMX8QXP_H
#define __APALIS_IMX8QXP_H

#include <linux/sizes.h>
#include <asm/arch/imx-regs.h>

#define CONFIG_REMAKE_ELF

#define CONFIG_ARCH_MISC_INIT
#define CONFIG_DISPLAY_BOARDINFO_LATE

#undef CONFIG_BOOTM_NETBSD

#define CONFIG_FSL_ESDHC
#define CONFIG_FSL_USDHC
#define CONFIG_SYS_FSL_ESDHC_ADDR       0
#define USDHC1_BASE_ADDR                0x5B010000
#define USDHC2_BASE_ADDR                0x5B020000
#define CONFIG_SUPPORT_EMMC_BOOT	/* eMMC specific */

#define CONFIG_ENV_OVERWRITE

#define CONFIG_ENV_VARS_UBOOT_RUNTIME_CONFIG

/* ENET Config */
#define CONFIG_MII

#define CONFIG_FEC_MXC
/* the on module PHY connects to the first ENET instance */
#define IMX_FEC_BASE			0x5B040000
#define CONFIG_FEC_MXC_PHYADDR		4
#define CONFIG_ETHPRIME			"eth0"

/* We have a slow phy... */
#define PHY_ANEG_TIMEOUT		15000

#define CONFIG_FEC_XCV_TYPE		RGMII
#define FEC_QUIRK_ENET_MAC

#define CONFIG_IP_DEFRAG
#define CONFIG_TFTP_BLOCKSIZE		4096
#define CONFIG_TFTP_TSIZE

#define CONFIG_IPADDR			192.168.10.2
#define CONFIG_NETMASK			255.255.255.0
#define CONFIG_SERVERIP			192.168.10.1

#define MEM_LAYOUT_ENV_SETTINGS \
	"fdt_addr_r=0x84000000\0" \
	"kernel_addr_r=0x82000000\0" \
	"ramdisk_addr_r=0x86400000\0" \
	"scriptaddr=0x86000000\0"

#ifdef CONFIG_AHAB_BOOT
#define AHAB_ENV "sec_boot=yes\0"
#else
#define AHAB_ENV "sec_boot=no\0"
#endif

/* Boot M4 */
#define M4_BOOT_ENV \
	"m4_0_image=m4_0.bin\0" \
	"loadm4image_0=fatload mmc ${mmcdev}:${mmcpart} ${loadaddr} ${m4_0_image}\0" \
	"m4boot_0=run loadm4image_0; dcache flush; bootaux ${loadaddr} 0\0" \

/* Enable Distro Boot */
#ifndef CONFIG_SPL_BUILD
#define BOOT_TARGET_DEVICES(func) \
        func(MMC, mmc, 1) \
        func(MMC, mmc, 0) \
        func(USB, usb, 0) \
        func(DHCP, dhcp, na)
#include <config_distro_bootcmd.h>
#undef CONFIG_ISO_PARTITION
#else
#define BOOTENV
#endif

#define FDT_FILE			"fsl-imx8qxp-apalis-eval-v3.dtb"

/* Initial environment variables */
#define CONFIG_EXTRA_ENV_SETTINGS \
	BOOTENV \
	M4_BOOT_ENV \
	AHAB_ENV \
	MEM_LAYOUT_ENV_SETTINGS \
	"bootcmd_mfg=fastboot 0\0" \
	"script=boot.scr\0" \
	"image=Image\0" \
	"panel=NULL\0" \
	"console=ttyLP1,115200 earlycon=lpuart32,0x5a040000,115200\0" \
	"fdt_addr=0x83000000\0"	\
	"boot_fdt=try\0" \
	"fdt_file=" FDT_FILE "\0" \
	"fdtfile=" FDT_FILE "\0" \
	"initrd_addr=0x83800000\0" \
	"initrd_high=0xffffffffffffffff\0" \
	"kernel_image=Image\0" \
	"mmcdev="__stringify(CONFIG_SYS_MMC_ENV_DEV)"\0" \
	"mmcpart=" __stringify(CONFIG_SYS_MMC_IMG_LOAD_PART) "\0" \
	"mmcroot=" CONFIG_MMCROOT " rootwait rw\0" \
	"mmcautodetect=yes\0" \
	"mmcargs=setenv bootargs console=${console},${baudrate} root=${mmcroot} " \
	"video=imxdpufb5:off video=imxdpufb6:off video=imxdpufb7:off\0" \
	"setup=run mmcargs\0"

/* Link Definitions */
#define CONFIG_LOADADDR			0x80280000

#define CONFIG_SYS_LOAD_ADDR		CONFIG_LOADADDR

#define CONFIG_SYS_INIT_SP_ADDR		0x80200000

#define CONFIG_SYS_MEMTEST_START	0x88000000
#define CONFIG_SYS_MEMTEST_END		0x89000000

/* Environment in eMMC, before config block at the end of 1st "boot sector" */
#define CONFIG_ENV_SIZE			0x2000
#define CONFIG_ENV_OFFSET		(-CONFIG_ENV_SIZE + \
					 CONFIG_TDX_CFG_BLOCK_OFFSET)
#define CONFIG_SYS_MMC_ENV_DEV		0
#define CONFIG_SYS_MMC_ENV_PART		1

#define CONFIG_SYS_MMC_IMG_LOAD_PART	1

/* On Apalis iMX8X USDHC1 is eMMC and USDHC2 is 4-bit SD */
#define CONFIG_MMCROOT			"/dev/mmcblk0p2"  /* USDHC1 eMMC */
#define CONFIG_SYS_FSL_USDHC_NUM	2

#define CONFIG_SYS_BOOTM_LEN		(64 << 20) /* Increase max gunzip size */

/* Size of malloc() pool */
#define CONFIG_SYS_MALLOC_LEN		((CONFIG_ENV_SIZE + (32*1024)) * 1024)

#define CONFIG_SYS_SDRAM_BASE		0x80000000
#define CONFIG_NR_DRAM_BANKS		3
#define PHYS_SDRAM_1			0x80000000
#define PHYS_SDRAM_2			0x880000000
#define PHYS_SDRAM_1_SIZE		0x80000000	/* 2 GB */
#define PHYS_SDRAM_2_SIZE		0x00000000	/* 0 GB */

/* Serial */
#define CONFIG_BAUDRATE			115200

/* Monitor Command Prompt */
#define CONFIG_SYS_PROMPT_HUSH_PS2	"> "
#define CONFIG_SYS_CBSIZE		2048
#define CONFIG_SYS_MAXARGS		64
#define CONFIG_SYS_BARGSIZE		CONFIG_SYS_CBSIZE
#define CONFIG_SYS_PBSIZE		(CONFIG_SYS_CBSIZE + \
					sizeof(CONFIG_SYS_PROMPT) + 16)

/* Generic Timer Definitions */
#define COUNTER_FREQUENCY		8000000	/* 8MHz */

#define CONFIG_IMX_SMMU

/* USB Config */
#ifdef CONFIG_CMD_USB
#define CONFIG_USB_MAX_CONTROLLER_COUNT 2

/* USB OTG controller configs */
#ifdef CONFIG_USB_EHCI_HCD
#define CONFIG_USB_HOST_ETHER
#define CONFIG_USB_ETHER_ASIX
#define CONFIG_MXC_USB_PORTSC		(PORT_PTS_UTMI | PORT_PTS_PTW)
#endif
#endif /* CONFIG_CMD_USB */

#ifdef CONFIG_USB_GADGET
#define CONFIG_USBD_HS
#endif

/* Framebuffer */
#ifdef CONFIG_VIDEO
#define CONFIG_VIDEO_IMXDPUV1
#define CONFIG_VIDEO_BMP_RLE8
#define CONFIG_SPLASH_SCREEN
#define CONFIG_SPLASH_SCREEN_ALIGN
#define CONFIG_BMP_16BPP
#define CONFIG_VIDEO_LOGO
#define CONFIG_VIDEO_BMP_LOGO
#define CONFIG_IMX_VIDEO_SKIP
#endif

#define CONFIG_OF_SYSTEM_SETUP
#define BOOTAUX_RESERVED_MEM_BASE 0x88000000
#define BOOTAUX_RESERVED_MEM_SIZE 0x08000000 /* Reserve from second 128MB */

#endif /* __APALIS_IMX8QXP_H */
