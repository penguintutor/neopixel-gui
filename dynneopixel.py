from rpi_ws281x import PixelStrip, Color
import _rpi_ws281x as ws

# Subclass of PixelStrip - adds the ability to make dynamic changes

class Dynamic_NeoPixel(PixelStrip):

    # Update all standard parameters for the LEDs
    def updSettings(self, settings):
        ws.ws2811_channel_t_count_set(self._channel, settings['ledcount'])
        ws.ws2811_channel_t_gpionum_set(self._channel, settings['gpiopin'])
        ws.ws2811_channel_t_invert_set(self._channel, 0 if not settings['ledinvert'] else 1)
        ws.ws2811_channel_t_brightness_set(self._channel, settings['ledmaxbrightness'])


    # These are changes that are more likely to be made on a regular basis
    def setBrightness(self, brightness):
        ws.ws2811_channel_t_brightness_set(self._channel, brightness)
        

