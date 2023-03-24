INSERT INTO flight(FlightNum, WeekNum, FlightDate, DepTime, ArrTime, Duration, DepEstAct, ArrEstAct, FlightStatus, Aircraft)
SELECT FlightNum, WeekNum+1, date_add(FlightDate, interval 7 day), DepTime, ArrTime, Duration, DepTime, ArrTime, 'On time', Aircraft
FROM flight
WHERE WeekNum = (SELECT MAX(WeekNum) FROM flight);

