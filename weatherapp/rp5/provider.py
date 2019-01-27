import urllib

from bs4 import BeautifulSoup

from weatherapp.core.abstract import WeatherProvider
from weatherapp.rp5 import config


class Rp5WeatherProvider(WeatherProvider):

    """ Provides weather info from rp5.ua site.
    """

    name = config.RP5_PROVIDER_NAME
    title = config.RP5_PROVIDER_TITLE

    def get_name(self):
        return self.name

    def get_default_location(self):
        return config.DEFAULT_RP5_LOCATION_NAME

    def get_default_url(self):
        return config.DEFAULT_RP5_LOCATION_URL

    def get_countries(self, countries_url):
        """ Gets countries list.
        """

        countries_page = self.get_page_source(countries_url)
        soup = BeautifulSoup(countries_page, 'html.parser')
        base = urllib.parse.urlunsplit(
            urllib.parse.urlparse(countries_url)[:2] + ('/', '', ''))
        countries = []
        for country in soup.find_all('div', class_='country_map_links'):
            url = urllib.parse.urljoin(base, country.find('a').attrs['href'])
            country = country.find('a').text
            countries.append((country, url))
        return countries

    def get_cities(self, country_url):
        """ Gets cities list.
        """

        cities = []
        cities_page = self. get_page_source(country_url)
        soup = BeautifulSoup(cities_page, 'html.parser')
        base = urllib.parse.urlunsplit(
            urllib.parse.urlparse(country_url)[:2] + ('/', '', ''))
        country_map = soup.find('div', class_='countryMap')
        if country_map:
            cities_list = country_map.find_all('h3')
            for city in cities_list:
                url = urllib.parse.urljoin(base, city.find('a').attrs['href'])
                city = city.find('a').text
                cities.append((city, url))
        return cities

    def configurate(self):
        """ Configures provider.
        """

        countries = self.get_countries(config.RP5_BROWSE_LOCATIONS)
        while countries:
            for index, country in enumerate(countries):
                print(f'{index + 1}. {country[0]}')
            try:
                selected_index = int(input('Please select country: '))
                country = countries[selected_index - 1]
                countries = self.get_countries(country[1])
            except IndexError:
                msg = 'Invalid number entered.'
                if self.app.options.debug:
                    self.app.logger.exception(msg)
                else:
                    self.app.logger.error(msg)
            except ValueError:
                msg = 'No number entered.'
                if self.app.options.debug:
                    self.app.logger.exception(msg)
                else:
                    self.app.logger.error(msg)

        cities = self.get_cities(country[1])
        while cities:
            for index, city in enumerate(cities):
                print(f'{index + 1}. {city[0]}')
            try:
                selected_index = int(input('Please select city: '))
                city = cities[selected_index - 1]
                cities = self.get_cities(city[1])
            except IndexError:
                msg = 'Invalid number entered.'
                if self.app.options.debug:
                    self.app.logger.exception(msg)
                else:
                    self.app.logger.error(msg)
            except ValueError:
                msg = 'No number entered.'
                if self.app.options.debug:
                    self.app.logger.exception(msg)
                else:
                    self.app.logger.error(msg)
        self.save_configuration(*city)

    def get_weather_info(self, page_content):
        """ Gets data from the site using the BeautifulSoup library.
        """

        city_page = BeautifulSoup(page_content, 'html.parser')
        current_day = city_page.find('div', id='archiveString')

        weather_info = {'cond': '', 'temp': '', 'feal_temp': '', 'wind': ''}
        if current_day:
            archive_info = current_day.find('div', class_='ArchiveInfo')
            if archive_info:
                archive_text = archive_info.text
                info_list = archive_text.split(',')
                weather_info['cond'] = info_list[1].strip()
                temp = archive_info.find('span', class_='t_0')
                if temp:
                    weather_info['temp'] = temp.text
                wind = info_list[2].strip()[:info_list[2].find(')') + 1]
                wind += info_list[4]
                if wind:
                    weather_info['wind'] = wind
        return weather_info