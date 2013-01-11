# -*- encoding: utf-8 -*-
#
# Copyright © 2012 New Dream Network, LLC (DreamHost)
#
# Author: Steven Berler <steven.berler@dreamhost.com>
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
"""Test getting the max resource volume.
"""

import datetime

from ceilometer.collector import meter
from ceilometer import counter

from ceilometer.openstack.common import cfg
from .base import FunctionalTest
from ceilometer.tests.db import require_map_reduce


class TestMaxResourceVolume(FunctionalTest):

    PATH = '/resources/resource-id/meters/volume.size/volume/max'

    def setUp(self):
        super(TestMaxResourceVolume, self).setUp()
        require_map_reduce(self.conn)

        self.counters = []
        for i in range(3):
            c = counter.Counter(
                'volume.size',
                'gauge',
                'GiB',
                5 + i,
                'user-id',
                'project1',
                'resource-id',
                timestamp=datetime.datetime(2012, 9, 25, 10 + i, 30 + i),
                resource_metadata={'display_name': 'test-volume',
                                   'tag': 'self.counter',
                                   }
                )
            self.counters.append(c)
            msg = meter.meter_message_from_counter(c,
                                                   cfg.CONF.metering_secret,
                                                   'source1',
                                                   )
            self.conn.record_metering_data(msg)

    def test_no_time_bounds(self):
        data = self.get_json(self.PATH)
        expected = {'volume': 7}
        assert data == expected

    def test_start_timestamp(self):
        data = self.get_json(
            self.PATH,
            extra_params={'daterange.start': '2012-09-25T11:30:00'})
        expected = {'volume': 7}
        assert data == expected

    def test_start_timestamp_after(self):
        data = self.get_json(
            self.PATH,
            extra_params={'daterange.start': '2012-09-25T12:34:00'})
        expected = {'volume': None}
        assert data == expected

    def test_end_timestamp(self):
        data = self.get_json(
            self.PATH,
            extra_params={'daterange.end': '2012-09-25T11:30:00'})
        expected = {'volume': 5}
        assert data == expected

    def test_end_timestamp_before(self):
        data = self.get_json(
            self.PATH,
            extra_params={'daterange.end': '2012-09-25T09:54:00'})
        expected = {'volume': None}
        assert data == expected

    def test_start_end_timestamp(self):
        data = self.get_json(
            self.PATH,
            extra_params={'daterange.start': '2012-09-25T11:30:00',
                          'daterange.end': '2012-09-25T11:32:00'})
        expected = {'volume': 6}
        assert data == expected
