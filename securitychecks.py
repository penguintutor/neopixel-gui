# These are all static methods (ie. not class) to perform security error checking

from response import Response


# return true if a valid integer - otherwise false
# Also updates the Response class addStatus
# error message is issued based on errormsg and whether it's greater than min / max
# if no min / max required then set to suitably huge values
# eg 1000000 is a huge number of LEDs to try and control using a single PWM channel
# Must already be converted to int first
def validateIntegerResponse (intval, parameter, min, max, response):

    if (intval < min):
        response.addStatus ("error", parameter, "Value of"+parameter+"is too small")
        return False
    elif (intval > max):
        response.addStatus ("error", parameter, "Value of"+parameter+"is too large")
        return False
    # Set status to success - if it fails to save then that will be in 'error' so the status is overridden by that
    else:
        response.addStatus ("success", parameter, "success")
    return True