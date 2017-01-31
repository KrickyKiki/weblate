# -*- coding: utf-8 -*-
#
# Copyright © 2012 - 2017 Michal Čihař <michal@cihar.com>
#
# This file is part of Weblate <https://weblate.org/>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

from __future__ import unicode_literals

from django.conf import settings

from weblate.trans.machine.base import MachineTranslation, MissingConfiguration


LANGUAGE_MAP = {
    'ca': 'cat',
    'cy': 'cym',
    'en': 'eng',
    'eo': 'epo',
    'gl': 'glg',
    'bs': 'hbs_BS',
    'is': 'isl',
    'es': 'spa',
}


class ApertiumAPYTranslation(MachineTranslation):
    '''
    Apertium machine translation support.
    '''
    name = 'Apertium APy'

    def __init__(self):
        '''
        Checks configuration.
        '''
        super(ApertiumAPYTranslation, self).__init__()
        self.url = self.get_server_url()

    def get_server_url(self):
        '''
        Returns URL of a server.
        '''
        if settings.MT_APERTIUM_APY is None:
            raise MissingConfiguration(
                'Not configured Apertium APy URL'
            )

        return settings.MT_APERTIUM_APY.rstrip('/')

    @property
    def all_langs(self):
        """Return all language codes known to service"""
        langs = self.supported_languages
        return set(
            [l[0] for l in langs] +
            [l[1] for l in langs]
        )

    def convert_language(self, language):
        '''
        Converts language to service specific code.
        '''
        # Force download of supported languages
        language = language.replace('-', '_')
        if language not in self.all_langs and language in LANGUAGE_MAP:
            return LANGUAGE_MAP[language]
        return language

    def download_languages(self):
        '''
        Downloads list of supported languages from a service.
        '''
        data = self.json_status_req('%s/listPairs' % self.url)
        return [
            (item['sourceLanguage'], item['targetLanguage'])
            for item in data['responseData']
        ]

    def is_supported(self, source, language):
        '''
        Checks whether given language combination is supported.
        '''
        return (source, language) in self.supported_languages

    def download_translations(self, source, language, text, unit, user):
        '''
        Downloads list of possible translations from Apertium.
        '''
        args = {
            'langpair': '%s|%s' % (source, language),
            'q': text,
        }
        if settings.MT_APERTIUM_KEY is not None:
            args['key'] = settings.MT_APERTIUM_KEY
        response = self.json_status_req(
            '%s/translate' % self.url,
            **args
        )

        return [(
            response['responseData']['translatedText'],
            100,
            self.name,
            text
        )]


class ApertiumTranslation(ApertiumAPYTranslation):
    '''
    Apertium machine translation support.
    '''
    name = 'Apertium'

    def get_server_url(self):
        return 'http://api.apertium.org/json'
