var formatJson = function (json, options) {
    var reg = null,
        formatted = '',
        pad = 0,
        PADDING = '    '; // one can also use '\t' or a different number of spaces

    // optional settings
    options = options || {};
    // remove newline where '{' or '[' follows ':'
    options.newlineAfterColonIfBeforeBraceOrBracket = (options.newlineAfterColonIfBeforeBraceOrBracket === true) ? true : false;
    // use a space after a colon
    options.spaceAfterColon = (options.spaceAfterColon === false) ? false : true;

    // begin formatting...
    if (typeof json !== 'string') {
        // make sure we start with the JSON as a string
        json = JSON.stringify(json);
    } else {
        // is already a string, so parse and re-stringify in order to remove extra whitespace
        json = JSON.parse(json);
        json = JSON.stringify(json);
    }

    // add newline before and after curly braces
    reg = /([\{\}])/g;
    json = json.replace(reg, '\r\n$1\r\n');

    // add newline before and after square brackets
    reg = /([\[\]])/g;
    json = json.replace(reg, '\r\n$1\r\n');

    // add newline after comma
    reg = /(\,)/g;
    json = json.replace(reg, '$1\r\n');

    // remove multiple newlines
    reg = /(\r\n\r\n)/g;
    json = json.replace(reg, '\r\n');

    // remove newlines before commas
    reg = /\r\n\,/g;
    json = json.replace(reg, ',');

    // optional formatting...
    if (!options.newlineAfterColonIfBeforeBraceOrBracket) {
        reg = /\:\r\n\{/g;
        json = json.replace(reg, ':{');
        reg = /\:\r\n\[/g;
        json = json.replace(reg, ':[');
    }
    if (options.spaceAfterColon) {
        reg = /\:/g;
        json = json.replace(reg, ':');
    }

    $.each(json.split('\r\n'), function (index, node) {
        var i = 0,
            indent = 0,
            padding = '';

        if (node.match(/\{$/) || node.match(/\[$/)) {
            indent = 1;
        } else if (node.match(/\}/) || node.match(/\]/)) {
            if (pad !== 0) {
                pad -= 1;
            }
        } else {
            indent = 0;
        }

        for (i = 0; i < pad; i++) {
            padding += PADDING;
        }

        formatted += padding + node + '\r\n';
        pad += indent;
    });

    return formatted;
};



//URL 编码,utf-8实现，同return encodeURIComponent(string);
//查看文章：http://www.ruanyifeng.com/blog/2010/02/url_encoding.html
var  urlEncode = function(string) {
	if(string == undefined || string == '') return '';
	var str = string.replace(/\r\n/g,"\n");
	var utftext = "";
	for (var n = 0; n < str.length; n++) {
		var c = str.charCodeAt(n);
		if (c < 128) {
			utftext += String.fromCharCode(c);
		}
		else if((c > 127) && (c < 2048)) {
			utftext += String.fromCharCode((c >> 6) | 192);
			utftext += String.fromCharCode((c & 63) | 128);
		}
		else {
			utftext += String.fromCharCode((c >> 12) | 224);
			utftext += String.fromCharCode(((c >> 6) & 63) | 128);
			utftext += String.fromCharCode((c & 63) | 128);
		}
	}
	utftext=utftext.replace('+','%2B');
	//utftext=utftext.replace(' ','%20');
	return escape(utftext);
}
var urlDecode = function(string) {
	if(string == undefined || string == '') return '';
	var utftext=unescape(string);
	var string = "";
	var i = 0;
	var c = c1 = c2 = 0;
	while ( i < utftext.length ) {
		c = utftext.charCodeAt(i);
		if (c < 128) {
			string += String.fromCharCode(c);
			i++;
		}
		else if((c > 191) && (c < 224)) {
			c2 = utftext.charCodeAt(i+1);
			string += String.fromCharCode(((c & 31) << 6) | (c2 & 63));
			i += 2;
		}
		else {
			c2 = utftext.charCodeAt(i+1);
			c3 = utftext.charCodeAt(i+2);
			string += String.fromCharCode(((c & 15) << 12) | ((c2 & 63) << 6) | (c3 & 63));
			i += 3;
		}
	}
	string=string.replace('%2B','+');
	return string;
}

function HTMLEnCode(str) {
	var s = "";
	if (str.length == 0)
		return "";
	s = str.replace(/&/g, "&amp;");
	s = s.replace(/</g, "&lt;");
	s = s.replace(/>/g, "&gt;");
	s = s.replace(/ /g, "&nbsp;");
	s = s.replace(/\'/g, "'");
	s = s.replace(/\"/g, "&quot;");
	s = s.replace(/\n/g, "<br>");
	return s;
}
function HTMLDeCode(str) {
	var s = "";
	if (str.length == 0)
		return "";
	s = str.replace(/&amp;/g, "&");
	s = s.replace(/&lt;/g, "<");
	s = s.replace(/&gt;/g, ">");
	s = s.replace(/&nbsp;/g, " ");
	s = s.replace(/'/g, "\'");
	s = s.replace(/&quot;/g, "\"");
	s = s.replace(/<br>/g, "\n");
	s = s.replace(/&ldquo;/g, "\"");
	s = s.replace(/&rdquo;/g, "\"");
	s = s.replace(/&rsquo;/g , "\"");
	s = s.replace(/&lsquo;/g , "\"");
	return s;
}



// 计算开始时间和结束时间的间隔时间。单位：ms
var calcDateInterval = function (startTime, endTime) {
    var startTimestamp = Date.parse(new Date(startTime));
    var endTimestamp = Date.parse(new Date(endTime));
    return endTimestamp - startTimestamp;
}


// 百度埋点
var _hmt = _hmt || [];
(function () {
    var hm = document.createElement("script");
    hm.src = "https://hm.baidu.com/hm.js?cc4cfa4ff149ccaa0b8ecf947647a702";
    var s = document.getElementsByTagName("script")[0];
    s.parentNode.insertBefore(hm, s);
})();

