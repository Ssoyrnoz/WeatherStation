var fileDisplayArea = document.getElementById("dataDump");
var sortedDat = document.getElementById("sortedDat");
var fileText;

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
                allText = rawFile.responseText;
        	fileText = alltext
	        fileDisplayArea.innerText = allText;
		fileDisplayArea.style.color = "orange";
            }
        }
    }
    rawFile.send(null);
}
readTextFile("./live.txt");

function sortData(rawData)
{
    sortedDat.innerText = fileText;
    sortedDat.style.color = "red";

    var dataList = allText.split(",");
    sortedDat.innerText = dataList.length+dataList;
    sortedDat.style.color = "yellow";

    var dataArr = [];
    for (var i = 0; i < dataList.length; i++) {
        sortedDat.innerText = dataList[i];
        sortedDat.style.color = "purple";
        var split = dataList[i].split('=');
        dataArr[split[0].trim()] = split[1].trim();
        }
    sortedDat.innerText = dataArr;
    sortedDat.style.color = "green";

    var timestamp = dataArr["timestamp"];

    var wind = dataArr["wind"];
    var windDir = dataArr["windDir"];
    var windGust = dataArr["windGust"];
    var windGustDir = dataArr["windGustDir"];
    var maxWind = dataArr["maxWind"];
    var maxWindTime = dataArr["maxWindTime"];
    var maxWindDir = dataArr["maxWindDir"];
    var maxGust = dataArr["maxGust"];
    var maxGustTime = dataArr["maxGustTime"];

    var humidity = dataArr["humidity"];
    var maxHum = dataArr["maxHum"];
    var maxHumTime = dataArr["maxHumTime"];
    var minHum = dataArr["minHum"];
    var minHumTime = dataArr["minHumTime"];

    var tempf = dataArr["tempf"];
    var dewpoint = dataArr["dewpoint"];
    var temp_max = dataArr["temp_max"];
    var temp_max_time = dataArr["temp_max_time"];
    var temp_min = dataArr["temp_min"];
    var temp_min_time = dataArr["temp_min_time"];

    var pressure = dataArr["pressure"];
    var maxPrs = dataArr["maxPrs"];
    var maxPrsTime = dataArr["maxPrsTime"];
    var minPrs = dataArr["minPrs"];
    var minPrsTime = dataArr["minPrsTime"];

    document.getElementById("timestamp").innerHTML = "Data current as of: "+timestamp;
}

function temp()
{
    // Temperature and Dewpoint in [F]
    tempDoc = document.getElementById("temp")

    if (temp < 32){
        tempDoc.style.color = "blue";}
    else if (temp >= 32 && temp < 37){
	tempDoc.style.color = "yellow";}
    else{
	tempDoc.style.color = "green";}

    tempDoc.innerHTML = "<a href='tempf.png'>Temp:</a> "+tempf+" [F]";
    document.getElementById("tempHigh").innerHTML = "  High Temp: "+temp_max+" at "+temp_max_time+
    "\r\n  Low Temp: "+temp_min+" at "+temp_min_time;

    var deltaDew = (temp - dewpoint)
    if (deltaDew < 5){
        document.getElementById("dewpoint").style.color = "red";}
    else if (deltaDew >= 5 && deltaDew < 10){
        document.getElementById("dewpoint").style.color = "yellow";}
    else{
        document.getElementById("dewpoint").style.color = "green";}
    document.getElementById("dewpoint").innerHTML = "<a href='tempf.png'>Dew Point:</a> "+dewpoint+" [F]";
}

function humidity()
{
    // Humidity in [%]
    if (humidity > 95){
        document.getElementById("humidity").style.color = "red";}
    else if (humidity > 80 && humidity <= 95){
        document.getElementById("humidity").style.color = "yellow";}
    else{
        document.getElementById("humidity").style.color = "green";}
    document.getElementById("humidity").innerHTML = "<a href='humidity.png'>Humidity:</a> "+humidity+" [%]";
    document.getElementById("humMax").innerHTML = "  Max Humidity: "+maxHum+" at "+maxHumTime+
    "\r\n  Min Humidity: "+minHum+" at "+minHumTime;
}

function pressure()
{
    //  Pressure in [atm]
    prsDoc = document.getElementById("pressure")
    prsDoc.innerHTML = "<a href='pressure.png'>Atmospheric Pressure:</a> "+pressure+" [atm]";
    prsDoc.style.color = "green";
    document.getElementById("maxPrs").innerHTML = "  Max Pressure: "+maxPrs+" at "+maxPrsTime+
    "\r\n  Min Pressure: "+minPrs+" at "+minPrsTime;
}

function wind()
{
    // Wind and Wind Gust in [mph]
    windDoc = document.getElementById("wind");
    windMaxDoc = document.getElementById("windMax");
    if (wind > 30){
        windDoc.style.color = "red";}
    else if (wind > 20 && wind <= 30){
        windDoc.style.color = "yellow";}
    else{
        windDoc.style.color = "green";}
    windDoc.innerHTML = "<a href='wind.png'>Wind Speed - 2min avg:</a> "+wind+" [mph] from "+windDir;
    windMaxDoc.innerHTML = "  Max Wind: "+maxWind+" at "+maxWindTime+
    "\n  Max Gust: "+maxGust+" at "+maxGustTime;
    windGustDoc = document.getElementById("windGust");
    if (windGust > 45){
        windGustDoc.style.color = "red";}
    else if (windGust > 35 && windGust <= 45){
        windGustDoc.style.color = "yellow";}
    else{
        windGustDoc.style.color = "green";}
    windGustDoc.innerHTML = "<a href='wind.png'>Wind Gust - 10min max:</a> "+windGust+" [mph] from "+windGustDir;
}
