# JSON controls

Controlled using POST method on 
/neopixel

## Commands - 'request':'command'


### sequence:sequence
Set sequence, returns success

### colours:colours
Set colours, returns success

### delay:delay
Set delay, returns success


## Queries - 'request':'query'
type:config / status
for config then use value: followed by config type eg. neopixels / server


## Update - 'request':'update'
Updates configuration
uses "type":"config" and "value":configtype (eg. neopixels)
(otherwise saveconfig doesn't exist)
reply can be error / warning / success
if success then saveconfig is updated to success as well
if serious error then 'error' is set with a message
if warning / less serious error then each of the entries is set to "success" or an error message



## Responses

### reply:code
Where code is success, failure (or warning), error description is provided using:
cmd:"***"
eg.
reply:error
sequence:Unable to set sequence

or
reply:warning
sequence:Sequence set to allon
colours:Unable to set colour