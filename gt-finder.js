var file_name = "freebies.txt";
var datasource = "C:\\Users\\EDITME\\Documents\\iMacros\\Datasources\\";
var eol = count_rows(datasource, file_name);
var row = 1;

iimPlay("CODE:URL GOTO=https://account.xbox.com/en-US/changegamertag?r="+Math.random())

for (var a=row; a < eol; a++)
{
    
    while (1){
        iimSet("row", a);
	var macro = "CODE:";
        macro += "SET !DATASOURCE "+file_name+"\n";
        macro += "SET !DATASOURCE_LINE {{row}}\n";
        macro += "TAG POS=1 TYPE=INPUT:TEXT ATTR=NAME:NewGamertag CONTENT={{!COL1}}\n";
        macro += "TAG POS=1 TYPE=INPUT:SUBMIT ATTR=*\n";
        macro += "TAG POS=2 TYPE=DIV ATTR=TXT:An<SP>error<SP>occurred.<SP>Please<SP>try<SP>again<SP>later. EXTRACT=TXT\n";
        iimPlay(macro);

        var last_extract = iimGetLastExtract().trim();
        if(last_extract == "" || last_extract == "NULL" || last_extract == " " || last_extract.includes("#EANF#")){
            break;
        }else{
    	    iimPlay("CODE:URL GOTO=https://account.xbox.com/en-US/changegamertag?r="+Math.random());
    	    iimPlay("CODE:WAIT SECONDS=60\n");
    	    continue;
        }
    }

    var macro = "CODE:TAG POS=1 TYPE=P ATTR=TXT:This<SP>gamertag<SP>is<SP>available.&&STYLE:*block* EXTRACT=TXT\n";
    iimPlay(macro);      

    var last_extract = iimGetLastExtract().trim();
    if(last_extract == "" || last_extract == "NULL" || last_extract == " " || last_extract.includes("#EANF#"))
    {
    	// uhmm...
    }else{
        iimSet("row", a);
        var macro = "CODE:";
        macro += "SET !DATASOURCE "+file_name+"\n";
        macro += "SET !DATASOURCE_LINE {{row}}\n";
        macro += "ADD !EXTRACT {{!COL1}}\n";
        macro += "SAVEAS TYPE=EXTRACT FOLDER=* FILE="+file_name+"\n";
        iimPlay(macro);
    }
 
    iimPlay("CODE:URL GOTO=https://account.xbox.com/en-US/changegamertag?r="+Math.random());
    
    time_wait = (Math.random() * (7.999 - 5.000) + 5.000).toFixed(3);
    iimPlay("CODE:WAIT SECONDS="+time_wait);
}

function count_rows(datasource,file_name)
{
    const CRLF = "\r\n";
    const LF = "\n";
	
    var lines = new Array();               
	
    var file_i = imns.FIO.openNode(datasource+file_name);
    var text = imns.FIO.readTextFile(file_i);
    var eol = (text.indexOf(CRLF) == -1) ? LF : CRLF;
	
    lines = text.split(eol);
    eol = lines.length;

    return eol;
}