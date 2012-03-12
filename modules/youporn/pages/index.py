# -*- coding: utf-8 -*-

# Copyright(C) 2010-2012 Romain Bignon
#
# This file is part of weboob.
#
# weboob is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# weboob is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with weboob. If not, see <http://www.gnu.org/licenses/>.


import re
import datetime

from weboob.capabilities.base import NotAvailable
from weboob.tools.capabilities.thumbnail import Thumbnail

from .base import PornPage
from ..video import YoupornVideo


__all__ = ['IndexPage']


class IndexPage(PornPage):
    def iter_videos(self):
        for li in self.document.getroot().xpath('//ul/li[@class="videoBox"]'):
            a = li.find('a')
            if a is None or a.find('img') is None:
                continue

            thumbnail_url = a.find('img').attrib['src']

            h1 = li.find('h1')
            a = h1.find('a')
            if a is None:
                continue

            url = a.attrib['href']
            _id = url[len('/watch/'):]
            _id = _id[:_id.find('/')]

            video = YoupornVideo(int(_id))
            video.title = a.text.strip()
            video.thumbnail = Thumbnail(thumbnail_url)

            hours = minutes = seconds = 0
            div = li.cssselect('h2[class=duration]')
            if len(div) > 0:
                pack = [int(s) for s in div[0].text.strip().split(':')]
                if len(pack) == 3:
                    hours, minutes, seconds = pack
                elif len(pack) == 2:
                    minutes, seconds = pack

            video.duration = datetime.timedelta(hours=hours, minutes=minutes, seconds=seconds)

            div = li.cssselect('div.stars')
            if div:
                m = re.match('.*star-(\d).*', div[0].attrib.get('class', ''))
                if m:
                    video.rating = int(m.group(1))
                    video.rating_max = 5

            video.set_empty_fields(NotAvailable, ('url', 'author'))

            yield video
