## Remote endpoint
To access remote endpoint, replace `localhost:8080` with `https://tribal-marker-274610.el.r.appspot.com`
## Register User
- http://localhost:8080/registerUser?uid=Chakki&fname=P&lname=Akka&phone=69&ccode=99&age=21&specz=Fire&pass=123
- required unique fields `phone` and `uid`
## Register Helpline
- http://localhost:8080/registerHelpline?hid=Chakki&hname=Akka&phone=69&ccode=99&specz=Fire&pass=123&loc=23.445,88.319
- required unique fields `phone` and `hid`
## Login
- http://localhost:8080/login?type=user&id=Alyigne&pass=Vishal_narnolia
- http://localhost:8080/login?type=help&id=ArSuu&pass=123
## Configure SOP - New
- http://localhost:8080/configureSOP?uid=Attri&guid_list=Chatto,TM,GuruDev
## Configure SOP - Update
- http://localhost:8080/configureSOP?uid=Attri&guid_list=Chatto,TM,GuruDev&update=yes
- `update` argument needed for update, not insert
## Raise Alarm
- http://localhost:8080/raiseAlarm?userID=Attri&alarmType=Fire&alarmLoc=22.57459442393395,88.43391573460059
## Check User Alerts (Notifs)
- http://localhost:8080/checkUserAlerts?uid=Alyigne
## Check Helpline Alerts (Notifs)
- http://localhost:8080/checkHelplineAlerts?hid=ArSuu
## Check User/Helpline ID exists
- http://localhost:8080/clientExists?type=help&id=Arsuu for helpline
- http://localhost:8080/clientExists?type=user&id=Thakuma for user
## Update user live location
- http://localhost:8080/liveLocation?uid=Chatto&loc=23.25,81.9
## Get all alarms
- http://localhost:8080/getAllAlarms
## Monitor a alert
- http://localhost:8080/monitorAlert?aid=ff05c116-9d99-11ea-b9f8-98fa9b07fff2