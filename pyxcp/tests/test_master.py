#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from unittest import mock

from pyxcp.master import Master
from pyxcp import transport


class TestMaster(unittest.TestCase):

    @mock.patch("pyxcp.transport.Eth")
    def testConnect(self, Eth):
        tr = Eth()
        tr.request.return_value = bytes(
            [0x1d, 0xc0, 0xff, 0xdc, 0x05, 0x01, 0x01])
        with Master(tr) as xm:
            res = xm.connect()
        self.assertEqual(res.maxCto, 255)
        self.assertEqual(res.maxDto, 1500)
        self.assertEqual(res.protocolLayerVersion, 1)
        self.assertEqual(res.transportLayerVersion, 1)
        self.assertEqual(res.resource.pgm, True)
        self.assertEqual(res.resource.stim, True)
        self.assertEqual(res.resource.daq, True)
        self.assertEqual(res.resource.calpag, True)
        self.assertEqual(res.commModeBasic.optional, True)
        self.assertEqual(res.commModeBasic.slaveBlockMode, True)
        self.assertEqual(res.commModeBasic.addressGranularity, 'BYTE')
        self.assertEqual(res.commModeBasic.byteOrder, 'INTEL')
        self.assertEqual(xm.maxCto, res.maxCto)
        self.assertEqual(xm.maxDto, res.maxDto)

    @mock.patch("pyxcp.transport.Eth")
    def testDisconnect(self, Eth):
        tr = Eth()
        tr.request.return_value = bytes([])
        with Master(tr) as xm:
            res = xm.disconnect()
        self.assertEqual(res, None)

    @mock.patch("pyxcp.transport.Eth")
    def testGetStatus(self, Eth):
        tr = Eth()
        tr.request.return_value = bytes([0x00, 0x1d, 0xff, 0x00, 0x00])
        with Master(tr) as xm:
            res = xm.getStatus()
        self.assertEqual(res.sessionConfiguration, 0)
        self.assertEqual(res.sessionStatus.resume, False)
        self.assertEqual(res.sessionStatus.daqRunning, False)
        self.assertEqual(res.sessionStatus.clearDaqRequest, False)
        self.assertEqual(res.sessionStatus.storeDaqRequest, False)
        self.assertEqual(res.sessionStatus.storeCalRequest, False)
        self.assertEqual(res.resourceProtectionStatus.pgm, True)
        self.assertEqual(res.resourceProtectionStatus.stim, True)
        self.assertEqual(res.resourceProtectionStatus.daq, True)
        self.assertEqual(res.resourceProtectionStatus.calpag, True)

    @mock.patch("pyxcp.transport.Eth")
    def testSync(self, Eth):
        tr = Eth()
        tr.request.return_value = bytes([0x00])
        with Master(tr) as xm:
            res = xm.synch()
        self.assertTrue(len(res) == 1)

    @mock.patch("pyxcp.transport.Eth")
    def testGetCommModeInfo(self, Eth):
        tr = Eth()
        tr.request.return_value = bytes(
            [0x00, 0x01, 0xff, 0x02, 0x00, 0x00, 0x19])
        with Master(tr) as xm:
            res = xm.getCommModeInfo()
        self.assertEqual(res.commModeOptional.interleavedMode, False)
        self.assertEqual(res.commModeOptional.masterBlockMode, True)
        self.assertEqual(res.maxbs, 2)
        self.assertEqual(res.minSt, 0)
        self.assertEqual(res.queueSize, 0)
        self.assertEqual(res.xcpDriverVersionNumber, 25)

    @mock.patch("pyxcp.transport.Eth")
    def testGetID(self, Eth):
        tr = Eth()
        tr.request.return_value = bytes(
            [0x00, 0x01, 0xff, 0x06, 0x00, 0x00, 0x00])
        with Master(tr) as xm:
            gid = xm.getID(0x01)
            tr.request.return_value = bytes(
                [0x58, 0x43, 0x50, 0x73, 0x69, 0x6d])
            res = xm.upload(gid.length)
        self.assertEqual(gid.mode, 0)
        self.assertEqual(gid.reserved, 65281)
        self.assertEqual(gid.length, 6)
        self.assertEqual(res, b'XCPsim')

    @mock.patch('socket.socket')
    @mock.patch('selectors.DefaultSelector')
    def testDownloadMax(self, mock_selector, mock_socket):
        mock_socket.return_value.recv.side_effect = [
            [0x01, 0x00, 0xff, 0x06], [0xff]]
        mock_selector.return_value.select.side_effect = [[(0, 1)], [(0, 1)]]

        tr = transport.Eth('localhost', loglevel="DEBUG")

        mock_socket.assert_called()
        mock_selector.assert_called()
        mock_selector.return_value.register.assert_called()

        with Master(tr) as xm:
            data = [0xCA, 0xFE, 0xBA, 0xBE]
            print("testDownloadMax: {} {}".format(len(data), data))
            xm.downloadMax(data)

        tr.close()

        mock_socket.return_value.send.assert_called_with(bytes(
            [0x05, 0x00, 0x00, 0x00, 0xee, 0xca, 0xfe, 0xba, 0xbe]))


def main():
    unittest.main()


if __name__ == '__main__':
    main()