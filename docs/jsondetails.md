###JSON controls

Controlled using POST method on 
/neopixel

##Commands - 'request':'command'


#sequence:sequence
Set sequence, returns success


##Queries - 'request':'query'




## Responses

#reply:code
Where code is success, failure (or warning), error description is provided using:
cmd:"***"
eg.
reply:error
sequence:Unable to set sequence

or
reply:warning
sequence:Sequence set to allon
colours:Unable to set colour