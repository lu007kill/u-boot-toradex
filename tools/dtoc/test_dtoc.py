#
# Copyright (c) 2012 The Chromium OS Authors.
#
# SPDX-License-Identifier:	GPL-2.0+
#

"""Tests for the dtb_platdata module

This includes unit tests for some functions and functional tests for
"""

import collections
import os
import struct
import unittest

import dtb_platdata
from dtb_platdata import conv_name_to_c
from dtb_platdata import get_compat_name
from dtb_platdata import get_value
from dtb_platdata import tab_to
import fdt
import fdt_util
import tools

our_path = os.path.dirname(os.path.realpath(__file__))


def get_dtb_file(dts_fname):
    """Compile a .dts file to a .dtb

    Args:
        dts_fname: Filename of .dts file in the current directory

    Returns:
        Filename of compiled file in output directory
    """
    return fdt_util.EnsureCompiled(os.path.join(our_path, dts_fname))


class TestDtoc(unittest.TestCase):
    """Tests for dtoc"""
    @classmethod
    def setUpClass(cls):
        tools.PrepareOutputDir(None)

    @classmethod
    def tearDownClass(cls):
        tools._RemoveOutputDir()

    def test_name(self):
        """Test conversion of device tree names to C identifiers"""
        self.assertEqual('serial_at_0x12', conv_name_to_c('serial@0x12'))
        self.assertEqual('vendor_clock_frequency',
                         conv_name_to_c('vendor,clock-frequency'))
        self.assertEqual('rockchip_rk3399_sdhci_5_1',
                         conv_name_to_c('rockchip,rk3399-sdhci-5.1'))

    def test_tab_to(self):
        """Test operation of tab_to() function"""
        self.assertEqual('fred ', tab_to(0, 'fred'))
        self.assertEqual('fred\t', tab_to(1, 'fred'))
        self.assertEqual('fred was here ', tab_to(1, 'fred was here'))
        self.assertEqual('fred was here\t\t', tab_to(3, 'fred was here'))
        self.assertEqual('exactly8 ', tab_to(1, 'exactly8'))
        self.assertEqual('exactly8\t', tab_to(2, 'exactly8'))

    def test_get_value(self):
        """Test operation of get_value() function"""
        self.assertEqual('0x45',
                         get_value(fdt.TYPE_INT, struct.pack('>I', 0x45)))
        self.assertEqual('0x45',
                         get_value(fdt.TYPE_BYTE, struct.pack('<I', 0x45)))
        self.assertEqual('0x0',
                         get_value(fdt.TYPE_BYTE, struct.pack('>I', 0x45)))
        self.assertEqual('"test"', get_value(fdt.TYPE_STRING, 'test'))
        self.assertEqual('true', get_value(fdt.TYPE_BOOL, None))

    def test_get_compat_name(self):
        """Test operation of get_compat_name() function"""
        Prop = collections.namedtuple('Prop', ['value'])
        Node = collections.namedtuple('Node', ['props'])

        prop = Prop(['rockchip,rk3399-sdhci-5.1', 'arasan,sdhci-5.1'])
        node = Node({'compatible': prop})
        self.assertEqual(('rockchip_rk3399_sdhci_5_1', ['arasan_sdhci_5_1']),
                         get_compat_name(node))

        prop = Prop(['rockchip,rk3399-sdhci-5.1'])
        node = Node({'compatible': prop})
        self.assertEqual(('rockchip_rk3399_sdhci_5_1', []),
                         get_compat_name(node))

        prop = Prop(['rockchip,rk3399-sdhci-5.1', 'arasan,sdhci-5.1', 'third'])
        node = Node({'compatible': prop})
        self.assertEqual(('rockchip_rk3399_sdhci_5_1',
                          ['arasan_sdhci_5_1', 'third']),
                         get_compat_name(node))

    def test_empty_file(self):
        """Test output from a device tree file with no nodes"""
        dtb_file = get_dtb_file('dtoc_test_empty.dts')
        output = tools.GetOutputFilename('output')
        dtb_platdata.run_steps(['struct'], dtb_file, False, output)
        with open(output) as infile:
            lines = infile.read().splitlines()
        self.assertEqual(['#include <stdbool.h>', '#include <libfdt.h>'], lines)

        dtb_platdata.run_steps(['platdata'], dtb_file, False, output)
        with open(output) as infile:
            lines = infile.read().splitlines()
        self.assertEqual(['#include <common.h>', '#include <dm.h>',
                          '#include <dt-structs.h>', ''], lines)

    def test_simple(self):
        """Test output from some simple nodes with various types of data"""
        dtb_file = get_dtb_file('dtoc_test_simple.dts')
        output = tools.GetOutputFilename('output')
        dtb_platdata.run_steps(['struct'], dtb_file, False, output)
        with open(output) as infile:
            data = infile.read()
        self.assertEqual('''#include <stdbool.h>
#include <libfdt.h>
struct dtd_sandbox_i2c_test {
};
struct dtd_sandbox_pmic_test {
\tbool\t\tlow_power;
\tfdt64_t\t\treg[2];
};
struct dtd_sandbox_spl_test {
\tbool\t\tboolval;
\tunsigned char\tbytearray[3];
\tunsigned char\tbyteval;
\tfdt32_t\t\tintarray[4];
\tfdt32_t\t\tintval;
\tunsigned char\tlongbytearray[9];
\tconst char *\tstringarray[3];
\tconst char *\tstringval;
};
struct dtd_sandbox_spl_test_2 {
};
''', data)

        dtb_platdata.run_steps(['platdata'], dtb_file, False, output)
        with open(output) as infile:
            data = infile.read()
        self.assertEqual('''#include <common.h>
#include <dm.h>
#include <dt-structs.h>

static struct dtd_sandbox_spl_test dtv_spl_test = {
\t.bytearray\t\t= {0x6, 0x0, 0x0},
\t.byteval\t\t= 0x5,
\t.intval\t\t\t= 0x1,
\t.longbytearray\t\t= {0x9, 0xa, 0xb, 0xc, 0xd, 0xe, 0xf, 0x10,
\t\t0x11},
\t.stringval\t\t= "message",
\t.boolval\t\t= true,
\t.intarray\t\t= {0x2, 0x3, 0x4, 0x0},
\t.stringarray\t\t= {"multi-word", "message", ""},
};
U_BOOT_DEVICE(spl_test) = {
\t.name\t\t= "sandbox_spl_test",
\t.platdata\t= &dtv_spl_test,
\t.platdata_size\t= sizeof(dtv_spl_test),
};

static struct dtd_sandbox_spl_test dtv_spl_test2 = {
\t.bytearray\t\t= {0x1, 0x23, 0x34},
\t.byteval\t\t= 0x8,
\t.intval\t\t\t= 0x3,
\t.longbytearray\t\t= {0x9, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
\t\t0x0},
\t.stringval\t\t= "message2",
\t.intarray\t\t= {0x5, 0x0, 0x0, 0x0},
\t.stringarray\t\t= {"another", "multi-word", "message"},
};
U_BOOT_DEVICE(spl_test2) = {
\t.name\t\t= "sandbox_spl_test",
\t.platdata\t= &dtv_spl_test2,
\t.platdata_size\t= sizeof(dtv_spl_test2),
};

static struct dtd_sandbox_spl_test dtv_spl_test3 = {
\t.stringarray\t\t= {"one", "", ""},
};
U_BOOT_DEVICE(spl_test3) = {
\t.name\t\t= "sandbox_spl_test",
\t.platdata\t= &dtv_spl_test3,
\t.platdata_size\t= sizeof(dtv_spl_test3),
};

static struct dtd_sandbox_spl_test_2 dtv_spl_test4 = {
};
U_BOOT_DEVICE(spl_test4) = {
\t.name\t\t= "sandbox_spl_test_2",
\t.platdata\t= &dtv_spl_test4,
\t.platdata_size\t= sizeof(dtv_spl_test4),
};

static struct dtd_sandbox_i2c_test dtv_i2c_at_0 = {
};
U_BOOT_DEVICE(i2c_at_0) = {
\t.name\t\t= "sandbox_i2c_test",
\t.platdata\t= &dtv_i2c_at_0,
\t.platdata_size\t= sizeof(dtv_i2c_at_0),
};

static struct dtd_sandbox_pmic_test dtv_pmic_at_9 = {
\t.low_power\t\t= true,
\t.reg\t\t\t= {0x9, 0x0},
};
U_BOOT_DEVICE(pmic_at_9) = {
\t.name\t\t= "sandbox_pmic_test",
\t.platdata\t= &dtv_pmic_at_9,
\t.platdata_size\t= sizeof(dtv_pmic_at_9),
};

''', data)

    def test_phandle(self):
        """Test output from a node containing a phandle reference"""
        dtb_file = get_dtb_file('dtoc_test_phandle.dts')
        output = tools.GetOutputFilename('output')
        dtb_platdata.run_steps(['struct'], dtb_file, False, output)
        with open(output) as infile:
            data = infile.read()
        self.assertEqual('''#include <stdbool.h>
#include <libfdt.h>
struct dtd_source {
\tstruct phandle_2_arg clocks[4];
};
struct dtd_target {
\tfdt32_t\t\tintval;
};
''', data)

        dtb_platdata.run_steps(['platdata'], dtb_file, False, output)
        with open(output) as infile:
            data = infile.read()
        self.assertEqual('''#include <common.h>
#include <dm.h>
#include <dt-structs.h>

static struct dtd_target dtv_phandle_target = {
\t.intval\t\t\t= 0x0,
};
U_BOOT_DEVICE(phandle_target) = {
\t.name\t\t= "target",
\t.platdata\t= &dtv_phandle_target,
\t.platdata_size\t= sizeof(dtv_phandle_target),
};

static struct dtd_target dtv_phandle2_target = {
\t.intval\t\t\t= 0x1,
};
U_BOOT_DEVICE(phandle2_target) = {
\t.name\t\t= "target",
\t.platdata\t= &dtv_phandle2_target,
\t.platdata_size\t= sizeof(dtv_phandle2_target),
};

static struct dtd_target dtv_phandle3_target = {
\t.intval\t\t\t= 0x2,
};
U_BOOT_DEVICE(phandle3_target) = {
\t.name\t\t= "target",
\t.platdata\t= &dtv_phandle3_target,
\t.platdata_size\t= sizeof(dtv_phandle3_target),
};

static struct dtd_source dtv_phandle_source = {
\t.clocks\t\t\t= {
\t\t\t{&dtv_phandle_target, {}},
\t\t\t{&dtv_phandle2_target, {11}},
\t\t\t{&dtv_phandle3_target, {12, 13}},
\t\t\t{&dtv_phandle_target, {}},},
};
U_BOOT_DEVICE(phandle_source) = {
\t.name\t\t= "source",
\t.platdata\t= &dtv_phandle_source,
\t.platdata_size\t= sizeof(dtv_phandle_source),
};

''', data)

    def test_aliases(self):
        """Test output from a node with multiple compatible strings"""
        dtb_file = get_dtb_file('dtoc_test_aliases.dts')
        output = tools.GetOutputFilename('output')
        dtb_platdata.run_steps(['struct'], dtb_file, False, output)
        with open(output) as infile:
            data = infile.read()
        self.assertEqual('''#include <stdbool.h>
#include <libfdt.h>
struct dtd_compat1 {
\tfdt32_t\t\tintval;
};
#define dtd_compat2_1_fred dtd_compat1
#define dtd_compat3 dtd_compat1
''', data)

        dtb_platdata.run_steps(['platdata'], dtb_file, False, output)
        with open(output) as infile:
            data = infile.read()
        self.assertEqual('''#include <common.h>
#include <dm.h>
#include <dt-structs.h>

static struct dtd_compat1 dtv_spl_test = {
\t.intval\t\t\t= 0x1,
};
U_BOOT_DEVICE(spl_test) = {
\t.name\t\t= "compat1",
\t.platdata\t= &dtv_spl_test,
\t.platdata_size\t= sizeof(dtv_spl_test),
};

''', data)

    def test_addresses64(self):
        """Test output from a node with a 'reg' property with na=2, ns=2"""
        dtb_file = get_dtb_file('dtoc_test_addr64.dts')
        output = tools.GetOutputFilename('output')
        dtb_platdata.run_steps(['struct'], dtb_file, False, output)
        with open(output) as infile:
            data = infile.read()
        self.assertEqual('''#include <stdbool.h>
#include <libfdt.h>
struct dtd_test1 {
\tfdt64_t\t\treg[2];
};
struct dtd_test2 {
\tfdt64_t\t\treg[2];
};
struct dtd_test3 {
\tfdt64_t\t\treg[4];
};
''', data)

        dtb_platdata.run_steps(['platdata'], dtb_file, False, output)
        with open(output) as infile:
            data = infile.read()
        self.assertEqual('''#include <common.h>
#include <dm.h>
#include <dt-structs.h>

static struct dtd_test1 dtv_test1 = {
\t.reg\t\t\t= {0x1234, 0x5678},
};
U_BOOT_DEVICE(test1) = {
\t.name\t\t= "test1",
\t.platdata\t= &dtv_test1,
\t.platdata_size\t= sizeof(dtv_test1),
};

static struct dtd_test2 dtv_test2 = {
\t.reg\t\t\t= {0x1234567890123456, 0x9876543210987654},
};
U_BOOT_DEVICE(test2) = {
\t.name\t\t= "test2",
\t.platdata\t= &dtv_test2,
\t.platdata_size\t= sizeof(dtv_test2),
};

static struct dtd_test3 dtv_test3 = {
\t.reg\t\t\t= {0x1234567890123456, 0x9876543210987654, 0x2, 0x3},
};
U_BOOT_DEVICE(test3) = {
\t.name\t\t= "test3",
\t.platdata\t= &dtv_test3,
\t.platdata_size\t= sizeof(dtv_test3),
};

''', data)

    def test_addresses32(self):
        """Test output from a node with a 'reg' property with na=1, ns=1"""
        dtb_file = get_dtb_file('dtoc_test_addr32.dts')
        output = tools.GetOutputFilename('output')
        dtb_platdata.run_steps(['struct'], dtb_file, False, output)
        with open(output) as infile:
            data = infile.read()
        self.assertEqual('''#include <stdbool.h>
#include <libfdt.h>
struct dtd_test1 {
\tfdt32_t\t\treg[2];
};
struct dtd_test2 {
\tfdt32_t\t\treg[4];
};
''', data)

        dtb_platdata.run_steps(['platdata'], dtb_file, False, output)
        with open(output) as infile:
            data = infile.read()
        self.assertEqual('''#include <common.h>
#include <dm.h>
#include <dt-structs.h>

static struct dtd_test1 dtv_test1 = {
\t.reg\t\t\t= {0x1234, 0x5678},
};
U_BOOT_DEVICE(test1) = {
\t.name\t\t= "test1",
\t.platdata\t= &dtv_test1,
\t.platdata_size\t= sizeof(dtv_test1),
};

static struct dtd_test2 dtv_test2 = {
\t.reg\t\t\t= {0x12345678, 0x98765432, 0x2, 0x3},
};
U_BOOT_DEVICE(test2) = {
\t.name\t\t= "test2",
\t.platdata\t= &dtv_test2,
\t.platdata_size\t= sizeof(dtv_test2),
};

''', data)

    def test_addresses64_32(self):
        """Test output from a node with a 'reg' property with na=2, ns=1"""
        dtb_file = get_dtb_file('dtoc_test_addr64_32.dts')
        output = tools.GetOutputFilename('output')
        dtb_platdata.run_steps(['struct'], dtb_file, False, output)
        with open(output) as infile:
            data = infile.read()
        self.assertEqual('''#include <stdbool.h>
#include <libfdt.h>
struct dtd_test1 {
\tfdt64_t\t\treg[2];
};
struct dtd_test2 {
\tfdt64_t\t\treg[2];
};
struct dtd_test3 {
\tfdt64_t\t\treg[4];
};
''', data)

        dtb_platdata.run_steps(['platdata'], dtb_file, False, output)
        with open(output) as infile:
            data = infile.read()
        self.assertEqual('''#include <common.h>
#include <dm.h>
#include <dt-structs.h>

static struct dtd_test1 dtv_test1 = {
\t.reg\t\t\t= {0x123400000000, 0x5678},
};
U_BOOT_DEVICE(test1) = {
\t.name\t\t= "test1",
\t.platdata\t= &dtv_test1,
\t.platdata_size\t= sizeof(dtv_test1),
};

static struct dtd_test2 dtv_test2 = {
\t.reg\t\t\t= {0x1234567890123456, 0x98765432},
};
U_BOOT_DEVICE(test2) = {
\t.name\t\t= "test2",
\t.platdata\t= &dtv_test2,
\t.platdata_size\t= sizeof(dtv_test2),
};

static struct dtd_test3 dtv_test3 = {
\t.reg\t\t\t= {0x1234567890123456, 0x98765432, 0x2, 0x3},
};
U_BOOT_DEVICE(test3) = {
\t.name\t\t= "test3",
\t.platdata\t= &dtv_test3,
\t.platdata_size\t= sizeof(dtv_test3),
};

''', data)

    def test_addresses32_64(self):
        """Test output from a node with a 'reg' property with na=1, ns=2"""
        dtb_file = get_dtb_file('dtoc_test_addr32_64.dts')
        output = tools.GetOutputFilename('output')
        dtb_platdata.run_steps(['struct'], dtb_file, False, output)
        with open(output) as infile:
            data = infile.read()
        self.assertEqual('''#include <stdbool.h>
#include <libfdt.h>
struct dtd_test1 {
\tfdt64_t\t\treg[2];
};
struct dtd_test2 {
\tfdt64_t\t\treg[2];
};
struct dtd_test3 {
\tfdt64_t\t\treg[4];
};
''', data)

        dtb_platdata.run_steps(['platdata'], dtb_file, False, output)
        with open(output) as infile:
            data = infile.read()
        self.assertEqual('''#include <common.h>
#include <dm.h>
#include <dt-structs.h>

static struct dtd_test1 dtv_test1 = {
\t.reg\t\t\t= {0x1234, 0x567800000000},
};
U_BOOT_DEVICE(test1) = {
\t.name\t\t= "test1",
\t.platdata\t= &dtv_test1,
\t.platdata_size\t= sizeof(dtv_test1),
};

static struct dtd_test2 dtv_test2 = {
\t.reg\t\t\t= {0x12345678, 0x9876543210987654},
};
U_BOOT_DEVICE(test2) = {
\t.name\t\t= "test2",
\t.platdata\t= &dtv_test2,
\t.platdata_size\t= sizeof(dtv_test2),
};

static struct dtd_test3 dtv_test3 = {
\t.reg\t\t\t= {0x12345678, 0x9876543210987654, 0x2, 0x3},
};
U_BOOT_DEVICE(test3) = {
\t.name\t\t= "test3",
\t.platdata\t= &dtv_test3,
\t.platdata_size\t= sizeof(dtv_test3),
};

''', data)