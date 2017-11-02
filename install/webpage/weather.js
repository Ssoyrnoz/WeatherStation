var fileDisplayArea = document.getElementById("dataDump");
var fileText = "";
var dataArr = [];

function pageTimer()
{
    var dataString = readTextFile("./live.txt");
    dataArr = sortData(dataString);
    temp(dataArr);
    humidity(dataArr);
    pressure(dataArr);
    wind(dataArr);
    var timer = setInterval(pageTimer, 10000);
}

function pageClock()
{
    var today = new Date();
    var utc_offset = today.getTimezoneOffset()/60
    var utc_sign
    if (utc_offset >= 0){
	utc_sign = "-";
    }
    else {
	utc_sign = "+";
    }
    var y = today.getFullYear();
    var mo = today.getMonth()+1;
    if (mo < 10){ mo = "0"+mo }
    var d = today.getDate();
    if (d < 10){ d = "0"+d }
    var h = today.getHours();
    if (h < 10){ h = "0"+h }
    var m = today.getMinutes();
    var s = today.getSeconds();
    m = checkTime(m);
    s = checkTime(s);
    document.getElementById('time').innerHTML =
    "Current time (UTC "+utc_sign+utc_offset+" Hr):  &nbsp; &nbsp; &nbsp; \r\n"+y+"-"+mo+"-"+d+" "+h + ":" + m + ":" + s;
}
function checkTime(i) {
    if (i < 10) {i = "0" + i};  // add zero in front of numbers < 10
    return i;
}


function calculateLST() {
    var longit = -122.637550;
    var tDate = new Date();
    var utSeconds    = tDate.getUTCSeconds();
    var utMinutes    = tDate.getUTCMinutes();
    var utHours      = tDate.getUTCHours();
    var utDay        = tDate.getUTCDate();
    var utMonth      = tDate.getUTCMonth() + 1;
    var utYear       = tDate.getUTCFullYear();
    var UT        = utHours + utMinutes/60 + utSeconds/3600;
    var LMST      = LM_Sidereal_Time(JulDay (utDay, utMonth, utYear, UT),longit);
    var GMST      = LM_Sidereal_Time(JulDay (utDay, utMonth, utYear, UT),0.0);

    var cuty = utYear.toString();
    var cutmo = utMonth.toString();
    if ( utMonth < 10) cutmo = "0" + utMonth.toString();
    var cutd = utDay.toString();
    if ( utDay < 10 ) cutd = "0" + utDay.toString();
    var cuth = utHours.toString();
    if ( utHours < 10 ) var cuth = "0" + utHours.toString(); 
    var cutm = utMinutes.toString()
    if ( utMinutes < 10 ) var cutm = "0" + utMinutes.toString(); 
    cuts = utSeconds.toString();
    if ( utSeconds < 10 ) var  cuts = "0" + utSeconds.toString(); 

    var h = Math.floor(LMST);
    var min = Math.floor(60.0*frac(LMST));
    var secs = Math.round(60.0*(60.0*frac(LMST)-min));
    if (secs == 60) {
     secs = 0;
     min = min + 1;
    }
    ch = h.toString();
    if ( h < 10 ) var ch = "0" + h.toString(); 
    cmin = min.toString()
    if ( min < 10 ) var cmin = "0" + min.toString(); 
    csecs = secs.toString();
    if ( secs < 10 ) var csecs = "0" + secs.toString(); 

    h = Math.floor(GMST);
    min = Math.floor(60.0*frac(GMST));
    secs = Math.round(60.0*(60.0*frac(GMST)-min));
    if (secs == 60) {
     secs = 0;
     min = min + 1;
    }
    gmt_ch = h.toString();
    if ( h < 10 ) var gmt_ch = "0" + h.toString(); 
    gmt_cmin = min.toString()
    if ( min < 10 ) var gmt_cmin = "0" + min.toString(); 
    gmt_csecs = secs.toString();
    if ( secs < 10 ) var gmt_csecs = "0" + secs.toString(); 


    var lst_clock = document.getElementById('lst_clock');
    lst_clock.innerHTML = "Local Sidereal Time (LST): &nbsp; &nbsp; &nbsp; &nbsp; &nbsp;        \r\n" +ch + ":"  + cmin  + ":" +csecs;
    var utc_clock = document.getElementById("utc_clock");
    utc_clock.innerHTML = "Coordinated Universal Time (UTC):&nbsp;\r\n"+cuty+"-"+cutmo+"-"+cutd+" " +cuth + ":"  +cutm+":"+cuts;
    pageClock();
    setTimeout("calculateLST()",997);
}

function LM_Sidereal_Time (jd, longitude) {
    var GMST = GM_Sidereal_Time(jd);		
    var LMST =  24.0*frac((GMST + longitude/15.0)/24.0);
    return LMST;
}

function GM_Sidereal_Time (jd) {	
    var t_eph, ut, MJD0, MJD;		
    MJD = jd - 2400000.5;		
    MJD0 = Math.floor(MJD);
    ut = (MJD - MJD0)*24.0;		
    t_eph  = (MJD0-51544.5)/36525.0;			
    return  6.697374558 + 1.0027379093*ut + (8640184.812866 + (0.093104 - 0.0000062*t_eph)*t_eph)*t_eph/3600.0;		
}

function JulDay (date, month, year, UT) {
    if (year<1900) year=year+1900
    if (month<=2) { month=month+12; year=year-1 }
    A = Math.floor(year/100);
    B = -13;
    JD =  Math.floor(365.25*(year+4716)) + Math.floor(30.6001*(month+1)) + date + B -1524.5 + UT/24.0;
    return JD
}

function frac(X) {
    X = X - Math.floor(X);
    if (X<0) X = X + 1.0;
    return X;		
}

function readTextFile(file)
{
    var rawFile = new XMLHttpRequest();
    rawFile.open("GET", file, false);
    rawFile.onreadystatechange = function ()
    {
        if(rawFile.readyState === 4)
        {
            if(rawFile.status === 200 || rawFile.status == 0)
            {
                //allText = rawFile.responseText;
        	//fileText = alltext
	        fileText = rawFile.responseText;
		//fileDisplayArea.innerText = fileText;
		//fileDisplayArea.style.color = "orange";
            }
        }
    }
    rawFile.send(null);
    return fileText;
}

function sortData(dataString)
{
    var sortedDat = document.getElementById("sortedDat");
    var dataList = dataString.split(',');
    sortedDat.innerText = typeof dataList;

    dataArr = [];
    for (var i = 0; i < dataList.length; i++) {
        sortedDat.innerText = dataList[i];
        sortedDat.style.color = "purple";
        var split = dataList[i].split('=');
        dataArr[split[0].trim()] = split[1].trim();
        }
    sortedDat.innerText = dataArr;
    sortedDat.style.color = "lime";

    var timestamp = dataArr["timestamp"];

    document.getElementById("timestamp").innerHTML = "Data current as of: \r\n"+timestamp;
    return dataArr;
}

function temp(dataArr)
{
    // Temperature and Dewpoint in [F]
    tempDoc = document.getElementById("temp")

    var tempf = dataArr["tempf"];
    var dewpoint = dataArr["dewpoint"];
    var temp_max = dataArr["temp_max"];
    var temp_max_time = dataArr["temp_max_time"];
    var temp_min = dataArr["temp_min"];
    var temp_min_time = dataArr["temp_min_time"];

    if (tempf < 32){
        tempDoc.style.color = "blue";}
    else if (tempf >= 32 && tempf < 37){
	tempDoc.style.color = "yellow";}
    else{
	tempDoc.style.color = "lime";}

    tempDoc.innerHTML = "<a href='tempf.png'>Temp:</a> "+tempf+" [F]";
    document.getElementById("tempHigh").innerHTML = "  High Temp: "+temp_max+" at "+temp_max_time+
    "\r\n  Low Temp: "+temp_min+" at "+temp_min_time;
    document.getElementById("tempHigh").style.color = "gray";


    var deltaDew = (tempf - dewpoint)
    if (deltaDew < 5){
        document.getElementById("dewpoint").style.color = "red";}
    else if (deltaDew >= 5 && deltaDew < 10){
        document.getElementById("dewpoint").style.color = "yellow";}
    else{
        document.getElementById("dewpoint").style.color = "lime";}
    document.getElementById("dewpoint").innerHTML = "<a href='tempf.png'>Dew Point:</a> "+dewpoint+" [F]";
}

function humidity(dataArr)
{
    // Humidity in [%]

    var humidity = dataArr["humidity"];
    var maxHum = dataArr["maxHum"];
    var maxHumTime = dataArr["maxHumTime"];
    var minHum = dataArr["minHum"];
    var minHumTime = dataArr["minHumTime"];

    if (humidity > 95){
        document.getElementById("humidity").style.color = "red";}
    else if (humidity > 80 && humidity <= 95){
        document.getElementById("humidity").style.color = "yellow";}
    else{
        document.getElementById("humidity").style.color = "lime";}
    document.getElementById("humidity").innerHTML = "<a href='humidity.png'>Humidity:</a> "+humidity+" [%]";
    document.getElementById("humMax").innerHTML = "  Max Humidity: "+maxHum+" at "+maxHumTime+
    "\r\n  Min Humidity: "+minHum+" at "+minHumTime;
    document.getElementById("humMax").style.color = "gray";
}

function pressure(dataArr)
{
    //  Pressure in [atm]

    var pressure = dataArr["pressure"];
    var maxPrs = dataArr["maxPrs"];
    var maxPrsTime = dataArr["maxPrsTime"];
    var minPrs = dataArr["minPrs"];
    var minPrsTime = dataArr["minPrsTime"];

    prsDoc = document.getElementById("pressure")
    prsDoc.innerHTML = "<a href='pressure.png'>Atmospheric Pressure:</a> "+pressure+" [atm]";
    prsDoc.style.color = "lime";
    document.getElementById("maxPrs").innerHTML = "  Max Pressure: "+maxPrs+" at "+maxPrsTime+
    "\r\n  Min Pressure: "+minPrs+" at "+minPrsTime;
    document.getElementById("maxPrs").style.color = "gray";
}

function wind(dataArr)
{
    // Wind and Wind Gust in [mph]
    windDoc = document.getElementById("wind");
    windMaxDoc = document.getElementById("windMax");

    var wind = dataArr["wind"];
    var windDir = dataArr["windDir"];
    var windGust = dataArr["windGust"];
    var windGustDir = dataArr["windGustDir"];
    var maxWind = dataArr["maxWind"];
    var maxWindTime = dataArr["maxWindTime"];
    var maxWindDir = dataArr["maxWindDir"];
    var maxGust = dataArr["maxGust"];
    var maxGustTime = dataArr["maxGustTime"];

    if (wind > 30){
        windDoc.style.color = "red";}
    else if (wind > 20 && wind <= 30){
        windDoc.style.color = "yellow";}
    else{
        windDoc.style.color = "lime";}
    windDoc.innerHTML = "<a href='wind.png'>Wind Speed - 2min avg:</a> "+wind+" [mph] from "+windDir;
    windMaxDoc.innerHTML = "  Max Wind: "+maxWind+" at "+maxWindTime+
    "\n  Max Gust: "+maxGust+" at "+maxGustTime;
    windMaxDoc.style.color = "gray";

    windGustDoc = document.getElementById("windGust");
    if (windGust > 45){
        windGustDoc.style.color = "red";}
    else if (windGust > 35 && windGust <= 45){
        windGustDoc.style.color = "yellow";}
    else{
        windGustDoc.style.color = "lime";}
    windGustDoc.innerHTML = "<a href='wind.png'>Wind Gust - 10min max:</a> "+windGust+" [mph] from "+windGustDir;
}
