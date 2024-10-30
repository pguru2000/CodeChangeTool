if(typeof window.debug_spintax == 'undefined') window.debug_spintax = true;
function Spinchecker() {

	/** PUBLIC PROPERTIES ************************************************************************/
	
	this.REFERENCE_RATE = { VARIATION: 1.85, PERFORATION: 0.8 };
	this.NB_MAX_CONSECUTIVE_WORDS_WITHOUT_VARIATIONS = 3;
	this.aStopWords = [];
	this.aUploadedFileNames = [];
	
	/** PRIVATE PROPERTIES ***********************************************************************/

	var _this = this,
		ERROR_MESSAGE = {
			CONSECUTIVE_WORDS_WITHOUT_VARIATIONS: { type:'WARNING', message:null },
			
			END_PUNCTUTAION_SIGN: { type:'WARNING', message:null },
			
			START_LOWER_CASE: { type:'WARNING', message:null },
			
			START_BLANK: { type:'WARNING', message:null },
			
			LINE_NUMBER: { type:'WARNING', message:null },
			SPINTAX_IS_EMPTY: { type:'ERROR', message:null },
			UNNECESSARY_OPENING_BRACKET_OR_MISSING_PIPE: { type:'ERROR', message:null },
			UNNECESSARY_CLOSING_BRACKET_OR_MISSING_PIPE: { type:'ERROR', message:null },
//			UNNECESSARY_OPENING_BRACKET: { type:'ERROR', message:null },
//			UNNECESSARY_CLOSING_BRACKET: { type:'ERROR', message:null },
			MISSING_MATCHING_OPENING_BRACKET_FOR_BRACKET: { type:'ERROR', message:null },
			MISSING_MATCHING_CLOSING_BRACKET_FOR_BRACKET: { type:'ERROR', message:null },
			MISSING_MATCHING_OPENING_BRACKET_FOR_PIPE: { type:'ERROR', message:null },
			MISSING_MATCHING_CLOSING_BRACKET_FOR_PIPE: { type:'ERROR', message:null }
		},
		HTML_TAG_STATUS = { OPENED: 1, ALMOST_CLOSED: 2, CLOSED: 3},
		justGageUniqueId = 1,
		PUBLIC_SITE_VERSION = false;
	
	/** PRIVATE METHODS **************************************************************************/
	
	/**
	 * @param	{string} spintax
	 * @return	{array of objects} each object looks like { type:"ERROR|WARNING", index:12, message:"..." }. Empty array if no errors where found 
	 */
	function searchSpintaxErrors(spintax) {
		var aErrors = [],
			oResult;
		if ( !spintax.length ) {
			aErrors.push($.extend({index:0}, ERROR_MESSAGE.SPINTAX_IS_EMPTY));
		}
		var example = spintax;
			var coordinates = example.split( "\n" );
			var resultsValidation = [];
			var sum=0;
			var k=0;
			var increm=0;
			for( var i = 0; i < coordinates.length; ++i ) {
			
				var strings = coordinates[i];
				var index_count = coordinates[i].length;
				k=i-1;
				increm++;
				sum += parseInt(coordinates[i].length);	
				//alert(sum);
				resultsValidation.push(sum);
						if(i !=0){
									var error_place=i;
									}else{
									var error_place=0;	
										}
					if (coordinates[i].charAt(0) == coordinates[i].charAt(0).toLowerCase() && coordinates[i].charAt(0) != "{" && coordinates[i].charAt(0) != " " && coordinates[i].charAt(0) != "<" && coordinates[i].charAt(1) != "<"){
						//alert(coordinates[i].charAt(0));
									if(i !=0){
									var error_place=i-1;
									var count_place=resultsValidation[error_place];	
									}else{
									var error_place=0;
									var count_place=0;
										}
										
										//alert(resultsValidation[error_place]);
										ERROR_MESSAGE.START_LOWER_CASE.message=ERROR_MESSAGE.LINE_NUMBER.message+increm+"&nbsp;:&nbsp;"+ERROR_MESSAGE.START_LOWER_CASE.message.toLowerCase();
									aErrors.push($.extend({index:count_place+i}, ERROR_MESSAGE.START_LOWER_CASE));
									ERROR_MESSAGE.START_LOWER_CASE.message=ERROR_MESSAGE.START_LOWER_CASE.message.replace(ERROR_MESSAGE.LINE_NUMBER.message+increm+"&nbsp;:&nbsp;","");
								}
					if (coordinates[i].charAt(0) == " " && coordinates[i].charAt(1) == "{"){
						
						//alert('yes');
						//alert(i);
									if(i !=0){
									var error_place=i-1;
									}else{
									var error_place=0;	
										}
										
									ERROR_MESSAGE.START_BLANK.message=ERROR_MESSAGE.LINE_NUMBER.message+increm+"&nbsp;:&nbsp;"+ERROR_MESSAGE.START_BLANK.message.toLowerCase();
									
									aErrors.push($.extend({index:resultsValidation[error_place]+i}, ERROR_MESSAGE.START_BLANK));
									
									ERROR_MESSAGE.START_BLANK.message=ERROR_MESSAGE.START_BLANK.message.replace(ERROR_MESSAGE.LINE_NUMBER.message+increm+"&nbsp;:&nbsp;","");
						}	
								var total_letters=coordinates[i].trim();
								var lastChar = total_letters.substr(total_letters.length - 1);
									
								if(lastChar != '}' && lastChar != '.' && lastChar != '!' && lastChar != '?' && lastChar != ':' && lastChar != '>'){
									//alert(lastChar);
									ERROR_MESSAGE.END_PUNCTUTAION_SIGN.message=ERROR_MESSAGE.LINE_NUMBER.message+increm+"&nbsp;:&nbsp;"+ERROR_MESSAGE.END_PUNCTUTAION_SIGN.message.toLowerCase();
									//alert(resultsValidation[error_place]);
									//alert(i);
									aErrors.push($.extend({index:resultsValidation[i]+i}, ERROR_MESSAGE.END_PUNCTUTAION_SIGN));
									
									ERROR_MESSAGE.END_PUNCTUTAION_SIGN.message=ERROR_MESSAGE.END_PUNCTUTAION_SIGN.message.replace(ERROR_MESSAGE.LINE_NUMBER.message+increm+"&nbsp;:&nbsp;","");
									
									}
				var count =0;					
				for (var l=0; l<strings.length; l++) {	
						if(i !=0){
									var error_place=i;
									}else{
									var error_place=0;	
										}
				switch(strings[l]) {
				case '{':
					oResult = findIndexOfMatchingClosingBracketForOpeningBracket(strings, l);
					if ( typeof oResult == "object" ) {
						var count =0;	
						if(i !=0){
							
							count = resultsValidation[error_place-1]+l+i;
							
							}else{
								
							count = l;	
							
								}
						//alert(increm);
						oResult.message=ERROR_MESSAGE.LINE_NUMBER.message+increm+"&nbsp;:&nbsp;"+oResult.message.toLowerCase();
						aErrors.push($.extend({index:count}, oResult));
						oResult.message=oResult.message.replace(ERROR_MESSAGE.LINE_NUMBER.message+increm+"&nbsp;:&nbsp;","");
					}
					break;
				case '}':
					oResult = findIndexOfMatchingOpeningBracketForClosingBracket(strings, l);
					if ( typeof oResult == "object" ) {
						var count =0;	
								if(i !=0){
							
							count = resultsValidation[error_place-1]+l+i;
							
							}else{
								
							count = l;	
							
								}
						oResult.message=ERROR_MESSAGE.LINE_NUMBER.message+increm+"&nbsp;:&nbsp;"+oResult.message.toLowerCase();
						aErrors.push($.extend({index:count}, oResult));
						oResult.message=oResult.message.replace(ERROR_MESSAGE.LINE_NUMBER.message+increm+"&nbsp;:&nbsp;","")
					}
					break;
				case '|':
					oResult = findIndexOfMatchingOpeningBracketForPipe(strings, l);
					if ( typeof oResult == "object" ) {
						var count =0;	
								if(i !=0){
									//alert(i);
									//alert(coordinates[0].length);
							//alert(resultsValidation[error_place-1]+l);
							count = resultsValidation[error_place-1]+l+i;
							//alert(resultsValidation[error_place-1]+l+i);
							}else{
								
							count = l;	
							
								}
//alert(l);
//alert(i);
						oResult.message=ERROR_MESSAGE.LINE_NUMBER.message+increm+"&nbsp;:&nbsp;"+oResult.message.toLowerCase();
						aErrors.push($.extend({index:count}, oResult));
						oResult.message=oResult.message.replace(ERROR_MESSAGE.LINE_NUMBER.message+increm+"&nbsp;:&nbsp;","")
					}
					oResult = findIndexOfMatchingClosingBracketForPipe(strings, l);
					if ( typeof oResult == "object" ) {
						var count =0;	
								if(i !=0){
							
							count = resultsValidation[error_place-1]+l+i;
							
							}else{
								
							count = l;	
							
								}
								
						oResult.message=ERROR_MESSAGE.LINE_NUMBER.message+increm+"&nbsp;:&nbsp;"+oResult.message.toLowerCase();
						
						aErrors.push($.extend({index:count}, oResult));
						
						oResult.message=oResult.message.replace(ERROR_MESSAGE.LINE_NUMBER.message+increm+"&nbsp;:&nbsp;","")
					}
					break;
			}
				}
   
			}
			
		$.merge(aErrors, findConsecutiveWordsUnspined(spintax));
		
		return aErrors;
	}
	
	/**
	 * @param	{string} spintax
	 * @param	{integer} index : index of an opening bracket
	 * @return	{object} if an error was found, {integer} otherwise
	 */
	function findIndexOfMatchingClosingBracketForOpeningBracket(spintax, index) {
		var depth = 0,
			pipeHavingSameDepthFound = false;
		for (var i=index+1; i<spintax.length; i++) {
			switch(spintax[i]) {
				case '{': depth++; break;
				case '}': if ( !depth-- ) { return ( pipeHavingSameDepthFound ? i : ERROR_MESSAGE.UNNECESSARY_OPENING_BRACKET_OR_MISSING_PIPE ) } break;
				case '|': if ( !depth ) { pipeHavingSameDepthFound = true; } break;
			}
		}
		//return ( pipeHavingSameDepthFound ? ERROR_MESSAGE.MISSING_MATCHING_CLOSING_BRACKET_FOR_BRACKET : ERROR_MESSAGE.UNNECESSARY_OPENING_BRACKET );
		return ( pipeHavingSameDepthFound ? ERROR_MESSAGE.MISSING_MATCHING_CLOSING_BRACKET_FOR_BRACKET : ERROR_MESSAGE.UNNECESSARY_OPENING_BRACKET_OR_MISSING_PIPE );
	}
	
	/**
	 * @param	{string} spintax
	 * @param	{integer} index : index of a pipe
	 * @return	{object} if an error was found, {integer} otherwise 
	 */
	function findIndexOfMatchingClosingBracketForPipe(spintax, index) {
		var depth = 0;
		for (var i=index+1; i<spintax.length; i++) {
			switch(spintax[i]) {
				case '{': depth++; break;
				case '}': if ( !depth-- ) { return i; } break;
			}
		}
		return ERROR_MESSAGE.MISSING_MATCHING_CLOSING_BRACKET_FOR_PIPE;
	}
	
	/**
	 * @param	{string} spintax
	 * @param	{integer} index : index of a closing bracket
	 * @return	{object} if an error was found, {integer} otherwise
	 */
	function findIndexOfMatchingOpeningBracketForClosingBracket(spintax, index) {
		var depth = 0,
			pipeHavingSameDepthFound = false;
		for (var i=index-1; i>=0; i--) {
			switch(spintax[i]) {
				case '{': if ( !depth-- ) { return ( pipeHavingSameDepthFound ? i : ERROR_MESSAGE.UNNECESSARY_CLOSING_BRACKET_OR_MISSING_PIPE ); } break;
				case '}': depth++; break;
				case '|': if ( !depth ) { pipeHavingSameDepthFound = true; } break;
			}
		}
//		return ( pipeHavingSameDepthFound ? ERROR_MESSAGE.MISSING_MATCHING_OPENING_BRACKET_FOR_BRACKET : ERROR_MESSAGE.UNNECESSARY_CLOSING_BRACKET );
		return ( pipeHavingSameDepthFound ? ERROR_MESSAGE.MISSING_MATCHING_OPENING_BRACKET_FOR_BRACKET : ERROR_MESSAGE.UNNECESSARY_CLOSING_BRACKET_OR_MISSING_PIPE );
	}
	
	/**
	 * @param	{string} spintax
	 * @param	{integer} index : index of a pipe
	 * @return	{object} if an error was found, {integer} otherwise
	 */
	function findIndexOfMatchingOpeningBracketForPipe(spintax, index) {
		var depth = 0;
		for (var i=index-1; i>=0; i--) {
			switch(spintax[i]) {
				case '{': if ( !depth-- ) { return i; } break;
				case '}': depth++; break;
			}
		}
		return ERROR_MESSAGE.MISSING_MATCHING_OPENING_BRACKET_FOR_PIPE;
	}
	
	/**
	 * @param	{string} spintax
	 * @return	{array of objects} each object looks like { index:45, type'WARNING', }
	 */
	function findConsecutiveWordsUnspined(spintax) {
		var aResult = [],
			searchingForConsecutiveWords = false,
			indexStartConsecutiveWords,
			currentWord = '',
			aReadWords = [],
			isCurrentWordBetweenChevrons = false,
			htmlTagStatus = HTML_TAG_STATUS.CLOSED,
			mayPushCurrentWordIntoArrayReadWords = function() {
//			console.log('*' + currentWord + '*', htmlTagStatus);
				if ( currentWord && !isCurrentWordBetweenChevrons && htmlTagStatus == HTML_TAG_STATUS.CLOSED ) {
					if ( isStopWord(currentWord) || isProperName(currentWord) || isVariable(currentWord) ) {
						mayAddElementToResult();
						searchingForConsecutiveWords = false;
						aReadWords = [];
					}
					else {
//						console.log('*' + currentWord + '*');
						aReadWords.push(currentWord);
					}
				}
			},
			mayAddElementToResult = function() {
				if ( aReadWords.length >= _this.NB_MAX_CONSECUTIVE_WORDS_WITHOUT_VARIATIONS ) {
//					console.log(aReadWords);
					aResult.push($.extend({ index:indexStartConsecutiveWords }, ERROR_MESSAGE.CONSECUTIVE_WORDS_WITHOUT_VARIATIONS ));
				}
			};

		for (var i=0; i<spintax.length; i++) {
			switch(spintax[i]) {
				case '{':
				case '|':
				case '}': 
				case '.':
				case '!':
				case '?':
				case '…':
				case '«':
				case '»':
				case '<':
				case '>':
					mayPushCurrentWordIntoArrayReadWords();
					if ( searchingForConsecutiveWords ) {
						searchingForConsecutiveWords = false;
						mayAddElementToResult();
						aReadWords = [];
					}
					switch ( spintax[i] ) {
						case "«": isCurrentWordBetweenChevrons = true; break;
						case "»": isCurrentWordBetweenChevrons = false; break;
						case "<":
							htmlTagStatus = HTML_TAG_STATUS.OPENED;
							break;
						case ">":
							if ( htmlTagStatus == HTML_TAG_STATUS.ALMOST_CLOSED ) {
								htmlTagStatus = HTML_TAG_STATUS.CLOSED;
							}
							break;
					}
					currentWord = '';
					break;
				
				case ' ':
				case ';':
				case ',':
				case ':':
				case '+':
				case '/':
				case "'":
				case "’":
				case '"':
					mayPushCurrentWordIntoArrayReadWords();
					currentWord = '';
					if ( spintax[i] == '/' && htmlTagStatus == HTML_TAG_STATUS.OPENED ) {
						htmlTagStatus = HTML_TAG_STATUS.ALMOST_CLOSED;
					}
					break;
					
				default :
					currentWord += spintax[i];
					if ( !searchingForConsecutiveWords ) {
						searchingForConsecutiveWords = true;
						indexStartConsecutiveWords = i;
					}
			}
		}
		mayPushCurrentWordIntoArrayReadWords();
		mayAddElementToResult();
  
		return aResult;
	}
	
	/**
	 * @param {string} word
	 * @return {boolean}
	 */
	function isStopWord(word) {
		return ( $.inArray(word.toLowerCase(), _this.aStopWords) != -1 );
	}
	
	/**
	 * @param {string} word
	 * @return {boolean}
	 */
	function isProperName(word) {
		return ( /[a-z]/i.test(word[0]) && word.ucFirst() == word );
	}
	
	/**
	 * @param {string} word
	 * @return {boolean}
	 */
	function isVariable(word) {
		return ( word[0] == "$" || word[0] == "#" );
	}
	
	/**
	 * @param	{integer} caretPosition : cursor's index in the current brackets block
	 * @return	{object} JSON looking like { indexOpeningBracket:21, indexOpeningBracket:32 } ; indexes values are set to -1 if no brackets are found 
	 */
	function findIndexesOfCurrentBracketsBlock(spintax, caretPosition) {
		var result = { indexOpeningBracket: -1, indexOpeningBracket: -1 },
			stopLooping,
			depth;
		
		// Index of the opening bracket
		depth = 0;
		stopLooping = false;
		for (var i=caretPosition-1; i>=0; i--) {
			if ( stopLooping ) {
				break;
			}
			switch(spintax[i]) {
				case '{': 
					if ( !depth-- ) { 
						result.indexOpeningBracket = i;
						stopLooping = true;
					} 
					break;
				case '}': depth++; break;
			}
		}
		if ( result.indexOpeningBracket == null ) {
			result.indexOpeningBracket = -1;
		}
		
		// Index of the closing bracket
		depth = 0;
		stopLooping = false;
		for (var i=caretPosition; i<spintax.length; i++) {
			if ( stopLooping ) {
				break;
			}
			switch(spintax[i]) {
				case '{': depth++; break;
				case '}': if ( !depth-- ) { 
					result.indexClosingBracket = i;
					stopLooping = true; 
				}
				break;
			}
		}
		if ( result.indexClosingBracket == null ) {
			result.indexClosingBracket = -1;
		}
		
		return result;
	}
	
	/**
	 * @param	{integer} noParagraph
	 * @param	{string} paragraphTitle
	 * @param	{string} paragraphContent
	 * @return	{object} paragraph content nested into the paragraph zone
	 */
	function createParagraphZone(noParagraph, paragraphTitle, paragraphContent) { if(true === window.debug_spintax) console.log('%c[createParagraphZone] - START', 'color:#F06');
		var para_type = 'NORMAL_PARAGRAPH';
		if(paragraphContent.toLowerCase().indexOf('meta title') > -1
		|| paragraphContent.toLowerCase().indexOf('meta-title') > -1) {
			para_type = 'META_TITLE';
		} else if(paragraphContent.toLowerCase().indexOf('meta description') > -1
		       || paragraphContent.toLowerCase().indexOf('meta-description') > -1) {
			para_type = 'META_DESCRIPTION';
		} else if(paragraphContent.toLowerCase().indexOf('<h1>') > -1
		       || paragraphContent.indexOf('H1') > -1 //|| paragraphContent.toLowerCase().indexOf('start-h1') > -1
		       || paragraphContent.toLowerCase().indexOf('titre h1') > -1) {
			para_type = 'H1_TITLE';
		} else if(paragraphContent.toLowerCase().indexOf('<h2>') > -1) {
			para_type = 'OTHER_TITLE';
		}
		var defaultPermutationMode = $('#default-permutation-mode').val(),
			$paragraphZone = $('' +
				'<div class="paragraph-container" data-title="' + paragraphTitle + '" data-paratype="' + para_type + '">' +
					'<div class="grid collapse-with-following">' +
						'<div class="unit half left-panel">' +
							'<label><span id="detected-elements-'+ noParagraph + '"></span>' + MySpeech.get("form.select.detected_element") + '</label>' +
						'</div>' +
						'<div class="unit half align-right right-panel">' +
							'<select name="cnt_par[' + noParagraph + '][permutation_mode]" id="permutation-mode-' + noParagraph + '" class="mini"  onChange="genRandomOption('+noParagraph+')">' +
								'<option value="ALL_NOT_PERMUTABLE">' + MySpeech.get("form.select.permutation_mode_none") + '</option>' +
								'<option value="ALL_PERMUTABLE">' + MySpeech.get("form.select.permutation_mode_all") + '</option>' +
								'<option value="ALL_PERMUTABLE_EXCEPT_FIRST">' + MySpeech.get("form.select.permutation_mode_all_except_first")+ '</option>' +
								
								'<option value="ALL_PERMUTABLE_EXCEPT_LAST">' + MySpeech.get("form.select.permutation_mode_all_except_last")+ '</option>' +
								
								'<option value="ALL_PERMUTABLE_EXCEPT_FIRST_LAST">' + MySpeech.get("form.select.permutation_mode_all_except_first_last")+ '</option>' +
							'</select>' +
							'<select name="cnt_par[' + noParagraph + '][permutation_pos]" id="permutation-pos-'+ noParagraph + '" class="mini para_rand_val" onChange="change_para_swap_box('+noParagraph+')">'+
								'<option value="META_TITLE"'+('META_TITLE' == para_type ? ' selected=""' : '')+'>' + MySpeech.get("form.select.meta_title") + '</option>'+
								'<option value="META_DESCRIPTION"'+('META_DESCRIPTION' == para_type ? ' selected=""' : '')+'>' + MySpeech.get("form.select.meta_description") + '</option>'+
								'<option value="H1_TITLE"'+('H1_TITLE' == para_type ? ' selected=""' : '')+'>' + MySpeech.get("form.select.h1_title") + '</option>'+
								'<option value="OTHER_TITLE"'+('OTHER_TITLE' == para_type ? ' selected=""' : '')+'>' + MySpeech.get("form.select.other_title") + '</option>'+
								'<option value="NORMAL_PARAGRAPH"'+('NORMAL_PARAGRAPH' == para_type ? ' selected=""' : '')+'>' + MySpeech.get("form.select.normal_paragraph") + '</option>'+
								'<option value="INTRO_PARAGRAPHP"'+('INTRO_PARAGRAPHP' == para_type ? ' selected=""' : '')+'>' + MySpeech.get("form.select.introduction_paragraph") + '</option>'+
								'<option value="CONCLUSION_PARAGRAPH"'+('CONCLUSION_PARAGRAPH' == para_type ? ' selected=""' : '')+'>' + MySpeech.get("form.select.conclusion_paragraph") + '</option>'+
							'</select>' +
						'</div>' +
						'<div class="grid random-opt-area align-right" id="random-opt-area-'+noParagraph+'">'+'<input type="checkbox" name="cnt_par_enabled_' + noParagraph + '" id="cnt_par_enabled_' + noParagraph + '" value="1" checked="" /><label for="cnt_par_enabled_' + noParagraph + '"></label>'+('OTHER_TITLE' == para_type ? '<label for="cnt_par_'+noParagraph+'_h2op_perm" style="display: inline"><input type="radio" name="cnt_par[' + noParagraph + '][h2op]" id="cnt_par_'+noParagraph+'_h2op_perm" value="prmnent" checked="" /> ' + MySpeech.get("form.select.permanenthtag") + '</label> &nbsp;&nbsp; <label for="cnt_par_'+noParagraph+'_h2op_rand" style="display: inline"><input type="radio" name="cnt_par[' + noParagraph + '][h2op]" id="cnt_par_'+noParagraph+'_h2op_rand" value="rndm" > ' + MySpeech.get("form.select.randmhtag") + '</label>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;' : '')+' '+MySpeech.get("form.select.min_ele_keep")+''+
						'<input type="text"  name="cnt_par[' + noParagraph + '][rand_from]" value="1" style="width:30px" placeholder="x-value"><input type="text"  name="cnt_par[' + noParagraph + '][rand_fr]" value="1" style="display:none" placeholder="x-value">'+
						'&nbsp;<span><span class="incrFrmVal_inner" style="font-size:x-large;cursor: pointer;">+</span>&nbsp;&nbsp;<span class="decrFrmVal_inner" style="font-size:x-large;cursor: pointer;">-</span></span> '+
						'&nbsp; '+MySpeech.get("form.select.upon")+' &nbsp;<input type="text" name="cnt_par[' + noParagraph + '][rand_to]" value="1" style="width:30px" placeholder="y-value"><input type="text" name="cnt_par[' + noParagraph + '][rand_t]" value="1" style="display:none" placeholder="y-value">'+
						'&nbsp;<span><span class="incrToVal_inner" style="font-size:x-large;cursor: pointer;">+</span>&nbsp;&nbsp;<span class="decrToVal_inner" style="font-size:x-large;cursor: pointer;">-</span></span>'+
						'<div style="clear:both;"></div>'+
						'<div id="btm-error" style="color:red;" align="right" style="padding:10px;"></div>'+
						'</div>'+
						
					'</div>' +
					'<div><input type="hidden" class= "extr" id="hidden-paragraph-' + noParagraph + '" name="cnt_par[' + noParagraph + '][p_contents]" value=""></div>'+
					'<div class="grid">' +
						'<div class="unit whole">' +
							'<div class="spintax-paragraph-wrapper">' +
								'<div class="db-toggle" data-title="' + MySpeech.get("message.spintax_paragraph") + '">' +
									'<div class="highlighter-container"></div>' +
                                     
									'<textarea id="spintax-paragraph-' + noParagraph + '" class="spintax autosize" rows="1">'+paragraphContent+'</textarea>' +
								'</div>' +
							'</div>' +
						'</div>' +
					'</div>' +
							
				'</div>');
		
		$paragraphZone.find('select.mini option[value="' + defaultPermutationMode + '"]').prop('selected', true);
		$('#spintax-article-container').css('display','none');
		$('#main-zone').after($paragraphZone);
		if(defaultPermutationMode == 'ALL_NOT_PERMUTABLE')
		{
		    $paragraphZone.find('.random-opt-area').css('display', 'none');
		}
		else
		{
		   $paragraphZone.find('.random-opt-area').css('display', 'block');
		}
		if(true === window.debug_spintax) console.log('%c[Flatspin.generateFlatspin] - START', 'color:#3D6');
		/*var readableContent    =  Flatspin.generateFlatspin(paragraphContent);
		readableContent        =  readableContent.trim();*/
		var countElement	   =  elementCountFlatspin(paragraphContent); // readableContent
		//var countElement       =  Flatspin.countReadbleElement(readableContent);
		if(true === window.debug_spintax) console.log('%c[Flatspin.generateFlatspin] - END', 'color:#3D6');
		
		$("#detected-elements-"+ noParagraph).html(countElement.actual);
		$paragraphZone.find('input[name="cnt_par['+noParagraph+'][rand_from]"]').val(countElement.total);
		$paragraphZone.find('input[name="cnt_par['+noParagraph+'][rand_to]"]').val(countElement.total);
		$paragraphZone.find('input[name="cnt_par['+noParagraph+'][rand_fr]"]').val(1);
		$paragraphZone.find('input[name="cnt_par['+noParagraph+'][rand_t]"]').val(countElement.total);
        
		//$("#hidden-paragraph-" + noParagraph).val(readableContent);
		/*saveTmpData(readableContent, noParagraph);*/
		saveTmpData_bypass(null/*readableContent*/, noParagraph); if(true === window.debug_spintax) console.log('%c[createParagraphZone] - END', 'color:#F06');
		return $('#spintax-paragraph-' + noParagraph).css('height', '1em').val(paragraphContent).textareaAutoSize();
	}
    
    
    function saveTmpDatasssss($content, $id) {
        var info = {
            content : $content,
            id : $id
        };
        $.ajax({
            url: 'save_data.php',
            type: 'POST',
            dataType: "json",
            data: info,
            success: function(data)
            {
                console.log('ok');
                //$('.loading-block').removeClass('open');
                //$('#hidden-paragraph-' + data.id).val(data.name);
               
            },
            error: function( data ){
               //console.log( data );
            }
        });
    }
    
    function muniqId() { 
        return Math.round(new Date().getTime() + (Math.random() * 100)); 
	};
	
	function saveTmpData_bypass( $content, $id ) {
		var name = 'content-' + $id + '-' + muniqId();
		var count = $( "form" ).data( "count" );
		if( count == undefined ) {
			total = 0;
		} else {
			total = count.total;
		}
		//console.log( count );
		//console.log( total );
		$("form").data( "count", { total: total + 1 } );
		if( ( total + 1 ) == $('input[id*="hidden-paragraph-"]').length ) {
			$('.loading-block').removeClass('open');
			$('#playaudio')[0].play();
		}
		$('#hidden-paragraph-' + $id).val(name);
	}
    
    function saveTmpData( $content, $id, cb ) { if(true === window.debug_spintax) console.log('%c[saveTmpData] - START ('+$id+')', 'color:#86B');
    	//console.log($id);
        var zip = new jszip(),
            name = 'content-' + $id + '-' + muniqId(),
            folder = $('form').find('input[name="folder"]').val();
            zip.file(name + ".txt", $content ); 
            zip.generateAsync({type:"blob"})
            .then(function(content) {
                var $date = new Date();
                    data = new File([content], name + ".zip"),
                    formData = new FormData();
                    formData.append('content', data);
                    formData.append('folder', folder);
                    $.ajax({
                        data: formData,
                        url: 'save_data.php',
                        type: 'POST',
                        processData: false,
                        contentType: false,
                        dataType: "html",
                        success: function(response) {
                            if( response == folder ) {
                                var count = $( "form" ).data( "count" );
                                if( count == undefined ) {
                                    total = 0;
                                } else {
                                    total = count.total;
                                }
                                //console.log( count );
                                //console.log( total );
                                $("form").data( "count", { total: total + 1 } );
                                if( ( total + 1 ) == $('input[id*="hidden-paragraph-"]').length ) {
                                    $('.loading-block').removeClass('open');
                                    $('#playaudio')[0].play();
                                }
                                $('#hidden-paragraph-' + $id).val(name);
                            } else {
                                $('body').append(response);
							}
							if(typeof cb == 'function')
								cb();
							if(true === window.debug_spintax) console.log('%c[saveTmpData] - END ('+$id+')', 'color:#86B');
                        }
                    });
            });
    };//DYANCORE.saveContent
	
	function prepareWarningsErrorsMessage(aErrors, spintax, noParagraph) {
		var message = '';
		$.each(aErrors, function(i, error) {
			if ( error != ERROR_MESSAGE.SPINTAX_IS_EMPTY ) {
				message += "<p class='" + error.type.toLowerCase() + "'>";
				message += ( error.type == 'ERROR' ? "<i title='" + MySpeech.get("message.error_uppercase") + "' class='fa fa-fw fa-exclamation-circle'></i>" : "<i title='" + MySpeech.get("message.warning_uppercase") + "' class='fa fa-fw fa-exclamation-circle'></i>");
				message += error.message;
				message += "</p>";
				message += "<div class='spintax'>" + formatSpintaxShownInErrorMessages(spintax, error.index, noParagraph, error) + "</div>";
			}
		});
		return message;
	}
	
	/**
	 * @param	{object} $paragraphContent
	 * @return
	 */
	function prepareParagraphStatsMessage($paragraphContent, noParagraph) {
		var spintax = $paragraphContent.val().trim(),
			oWordsStats = getWordsStats(spintax),
			nbParagraphElements = spintax.split('\n').length,
			nbResults = getNbResultsForParagraph(spintax, $('#permutation-mode-' + noParagraph ).val(), true);

		return '' +
			'<div class="grid">' +
				'<div class="unit three-fifths">' +
					'<div class="stats-resume">' +
						MySpeech.get("message.paragraph_number") + " " + noParagraph + " " + MySpeech.get("message.contains") + " " + nbParagraphElements + " " + MySpeech.get("message.element") + (nbParagraphElements > 1 ? 's' : '') + " " + MySpeech.get("message.having_permutation_mode") + MySpeech.get("message.having_quote_arrow_pre") +"" + $('#permutation-mode-' + noParagraph + ' option:selected').text().lcFirst() + MySpeech.get("message.having_quote_arrow_nex")+". " +
						MySpeech.get("message.results_total_is") + " " + ( nbResults == Infinity || isNaN(nbResults) ? MySpeech.get("message.close_to_infinity") :  nbResults ) + ". " +
						MySpeech.get("message.paragraph_has_replacement_rate") + " " + ( isNaN(oWordsStats.variationRate) ? MySpeech.get("message.close_to_infinity") : MySpeech.get("message.of") + " " + new String(oWordsStats.variationRate).replace('.', MySpeech.get("message.having_seprator_avg")) + "% " ) + " " +
						MySpeech.get("message.and_hole_rate") + " " + ( isNaN(oWordsStats.perforationRate) ? MySpeech.get("message.close_to_infinity") : MySpeech.get("message.of") + " " + new String(oWordsStats.perforationRate).replace('.', MySpeech.get("message.having_seprator_avg")) + "%" ) + "." +
					'</div>' +
				'</div>' +
				/*'<div class="unit two-fifths align-right">' +
					'<div class="gauge spinchecker" data-gauge-value="' + (isNaN(oWordsStats.variationIndex) ? 0 : oWordsStats.variationIndex) + '"></div>' +
					'<div class="gauge spinchecker" data-gauge-value="' + (isNaN(oWordsStats.perforationIndex) ? 0 : oWordsStats.perforationIndex) + '"></div>' +
					'<div class="gauge spinchecker" data-gauge-value="' + (isNaN(oWordsStats.qualityIndex) ? 0 : oWordsStats.qualityIndex) + '"></div>' +
				'</div>' +*/
			'</div>';
	}
	
	/**
	 * @deprecated
	 * @param	{string} spintax
	 * @return	{integer} spin rate in percents
	 */
	function getSpinRate(spintax) {
		var tree = SpinerMan.buildTree(spintax);
		return ((tree.s.w > 0 && tree.r > 0) ? (100 * tree.s.r / (tree.s.w / tree.r)).toFixed(1) : 0);
	}
	
	/**
	 * @deprecated
	 * @param	{string} paragraphSpintax
	 * @param	{stringr} permutationMode : ALL_PERMUTABLE / ALL_NOT_PERMUTABLE / ALL_PERMUTABLE_EXCEPT_FIRST
	 * @return	{string} 
	 */
	function getParagraphSpintaxWithParagraphElementsPermutations(paragraphSpintax, permutationMode) {
		switch(permutationMode) {
			case 'ALL_PERMUTABLE':
				var aParagraphElements = paragraphSpintax.split('\n');
				return generateSpintaxCombination(aParagraphElements);
			case 'ALL_NOT_PERMUTABLE':
				return paragraphSpintax;
			case 'ALL_PERMUTABLE_EXCEPT_FIRST':
				var aParagraphElements = paragraphSpintax.split('\n');
				return aParagraphElements.shift() + ' ' + generateSpintaxCombination(aParagraphElements);
			default:
				alert("Function getParagraphSpintaxWithParagraphElementsPermutations() : ERROR !! permutationMode : " + permutationMode);
		}
	}
	
	/**
	 * @deprecated
	 * @param	{string} aSpintaxSentences
	 * @return	{string}
	 */
	function generateSpintaxCombination(aSpintaxSentences) { 
		switch (aSpintaxSentences.length) {
			case 0: return '';
			case 1: return aSpintaxSentences[0];
			default:
				var aCombinations = Combinatorics.permutation(aSpintaxSentences).toArray(),
					spintaxResult = '';
				$.each(aCombinations, function(i,v) {
					spintaxResult += ( !i ? '' : '|') + v.join(' ');
				});
				return '{' + spintaxResult + '}';
		}
	}
	
//	/**
//	 * @param	{string} aSpintaxSentences
//	 * @param	{objet, optional} $clickedButton
//	 * @return	{string}
//	 */
//	function AJAX_generateSpintaxCombination(aSpintaxSentences, $clickedButton) {
//		var clickedButtonLabel = ( $clickedButton != undefined ? $clickedButton.html() : null );
//		return $.ajax({
//			type: 'POST',
//			url: 'php/ajax/generate-spintax-combination.php',
//			async: false,
//			data: { aSpintaxSentences: aSpintaxSentences },
//			beforeSend: function(jqXHR, settings) {
//				if ( $clickedButton != undefined ) {
//					$clickedButton.html('<img src="images/ajax-loader.gif" style="padding-right:10px">Traitement en cours&hellip;').removeClass('action').addClass('disabled');
//				}
//			},
//			success: function(jsonResponse) {
//				if ( $clickedButton != undefined ) {
//					$clickedButton.html(clickedButtonLabel).removeClass('disabled').addClass('action');
//				}
//			},
//			error: function(request, error) {
//				showServerErrorNotification(request);
//			}
//		}).responseJSON;
//	}
	
	/**
	 * @param	{string} spintax
	 * @param	{boolean, optional} formatBigNumber
	 * @return	{integer} nb of permutations
	 */
	function getNbResults(spintax, formatBigNumber) {
		var tree = SpinerMan.buildTree(spintax);
		return ( formatBigNumber !== undefined && formatBigNumber ? new String(tree.r).formatBigNumber() : tree.r );
	}
	
	/**
	 * @param	{string} paragraphSpintax
	 * @param	{stringr} permutationMode : ALL_NOT_PERMUTABLE / ALL_PERMUTABLE / ALL_PERMUTABLE_EXCEPT_FIRST
	 * @param	{boolean, optional} formatBigNumber
	 * @return	{integer} 
	 */
	function getNbResultsForParagraph(paragraphSpintax, permutationMode, formatBigNumber) {
		var result;
		
		paragraphSpintax = paragraphSpintax.trim();
		switch(permutationMode) {
			case 'ALL_NOT_PERMUTABLE':
				result = getNbResults(paragraphSpintax);
				break;
			case 'ALL_PERMUTABLE':
			case 'ALL_PERMUTABLE_EXCEPT_FIRST':
				var aParagraphElements = paragraphSpintax.split('\n'), result;
				switch (aParagraphElements.length) {
					case 0: result = 0; break;
					case 1: result = getNbResults(aParagraphElements[0]); break;
					default:
						if ( permutationMode == 'ALL_PERMUTABLE_EXCEPT_FIRST' ) {
							result = getNbResults(aParagraphElements[0]); 
							aParagraphElements.shift();
						}
						else {
							result = 1;
						}
						result *= factorial(aParagraphElements.length);
						$.each(aParagraphElements, function(i,v) {
							result *= getNbResults(v);
						});
				}
			break;
			
			case 'ALL_PERMUTABLE_EXCEPT_LAST':
			var aParagraphElements = paragraphSpintax.split('\n'), result;
				switch (aParagraphElements.length) {
					case 0: result = 0; break;
					case 1: result = getNbResults(aParagraphElements[0]); break;
					default:
						if ( permutationMode == 'ALL_PERMUTABLE_EXCEPT_LAST' ) {
							result = getNbResults(aParagraphElements[0]); 
							aParagraphElements.pop();
						}
						else {
							result = 1;
						}
						result *= factorial(aParagraphElements.length);
						$.each(aParagraphElements, function(i,v) {
							result *= getNbResults(v);
						});
				}
			break;
			
			case 'ALL_PERMUTABLE_EXCEPT_FIRST_LAST':
			var aParagraphElements = paragraphSpintax.split('\n'), result;
				switch (aParagraphElements.length) {
					case 0: result = 0; break;
					case 1: result = getNbResults(aParagraphElements[0]); break;
					default:
						if ( permutationMode == 'ALL_PERMUTABLE_EXCEPT_FIRST_LAST' ) {
							result = getNbResults(aParagraphElements[0]); 
							aParagraphElements.shift();
							aParagraphElements.pop();
						}
						else {
							result = 1;
						}
						result *= factorial(aParagraphElements.length);
						$.each(aParagraphElements, function(i,v) {
							result *= getNbResults(v);
						});
				}
			break;	
			default:
				result = 0;
				alert("Function getNbResultsForParagraph() : ERROR !! Bad permutationMode : " + permutationMode);
		}
		return ( formatBigNumber !== undefined && formatBigNumber ? new String(result).formatBigNumber() : result );
	}
	
	/**
	 * @param	{string} articleSpintax
	 * @param	{boolean} formatBigNumber
	 * @return	{integer} 
	 */
	function getNbResultsForArticle(articleSpintax, formatBigNumber) {
		var aParagraphsContents, 
			result,
			resultLimit = Math.pow(10,12);
		
		articleSpintax = articleSpintax.trim();
		aParagraphsContents = articleSpintax.split('\n\n');
		switch (aParagraphsContents.length) {
			case 0: result = 0; break;
			case 1: result = getNbResults(aParagraphsContents[0]); break;
			default:
				var noParagraph;
				result = factorial(aParagraphsContents.length);
				$.each(aParagraphsContents, function(i,v) {
					noParagraph = i+1;
					result *= getNbResultsForParagraph(v, $('#permutation-mode-' + noParagraph ).val());
					if ( result > resultLimit ) {
						return false;
					}
				});
		}
		return ( formatBigNumber !== undefined && formatBigNumber ? new String(result).formatBigNumber() : result );
	}
	
	/**
	 * @param	{string} spintax
	 * @return	{object} of type { minWords:3, maxWords:50, avgWords:22.6 }
	 */
	function getWordsStats(spintax) {
		var result = SpinerMan.getStats(SpinerMan.buildTree(spintax));
		
		result.variationRate = parseFloat((( result.totalVariations / result.avgWords ) * 100 ).toFixed(1));
		result.variationIndex = parseFloat((( result.totalVariations / result.avgWords ) / _this.REFERENCE_RATE.VARIATION ).toFixed(1));
		
		result.perforationRate = parseFloat((( result.totalHoles / result.avgWords ) * 100 ).toFixed(1));
		result.perforationIndex = parseFloat((( result.totalHoles / result.avgWords ) / _this.REFERENCE_RATE.PERFORATION ).toFixed(1));
		
//		result.qualityIndex = ( !result.totalHoles ? 0 : parseFloat((( result.totalVariations / result.totalHoles ) / ( _this.REFERENCE_RATE.VARIATION / _this.REFERENCE_RATE.PERFORATION )).toFixed(1)) );
		result.qualityIndex = ( !result.totalHoles ? 0 : parseFloat( (result.perforationIndex * ((result.totalHoles/result.totalVariations) / (_this.REFERENCE_RATE.PERFORATION/_this.REFERENCE_RATE.VARIATION))).toFixed(1) ) );
		
		return result;
	}

	/* DEPRECATED / NOT IN USE
	function generateTheArticles(e) {
		e.preventDefault();
		var $form = $('#db-form'),
			form_data_serialized = $form.serialize();
		if($form.hasClass('processing')) {
			MyUtils.displayInfoMessage('warning', 'Generation of articles is in progress...');
			return false;
		}
		$form.addClass('processing');
		$.ajax({
			url: 'generate-the-articles.php',
			data: form_data_serialized,
			dataType: 'json',
			method: 'POST',
			context: $form
		}).done(function(response) {
			console.log(response);
			//MyUtils.displayInfoMessage('success', MySpeech.get("form.label.spintax_uploaded"));
		}).fail(function(error) {
			console.log(error.responseJSON, error.status);
			MyUtils.displayInfoMessage('warning', typeof error.responseJSON.message == 'undefined' ? 'A fatal error has occurred while generating articles.' : error.responseJSON.message);
		}).always(function() {
			$form.removeClass('processing');
		});
		return false;
	}*/
	
	/**
	 * @param	none
	 * @return	none
	 */
	 
	function getReadbleContent() {
	   	$("#db-form").removeAttr("onsubmit");
		$("#db-form").submit();
		return false;
	}

	/**
	 * @param	{Object} $infoMessage
	 * @return	none 
	 */
	function renderThreeGauges($infoMessage) {
		var maxValue = 0;
		
		$infoMessage.find('.gauge').each(function() {
			if ( parseFloat($(this).attr('data-gauge-value')) > maxValue ) {
				maxValue = parseFloat($(this).attr('data-gauge-value'));
			}
		});
		renderGauge($infoMessage.find('.gauge').eq(0), MySpeech.get("message.replacement_index"), maxValue);
		renderGauge($infoMessage.find('.gauge').eq(1), MySpeech.get("message.hole_index"), maxValue);
		renderGauge($infoMessage.find('.gauge').eq(2), MySpeech.get("message.quality_index"), maxValue);
	}
	
	/**
	 * @param	{Object} $toggleWrapper
	 * @return	none
	 */
	function openToggleIfClosed($toggleWrapper) {
		var $toggle = $toggleWrapper.find('.db-toggle');
		if ( $toggle.hasClass('closed') ) {
			openToggle($toggle, $.noop );
		}
	}
	
	function closeToggleIfOpened($infoMessageWrapper) {
		var $toggle = $infoMessageWrapper.find('.db-toggle');
		if ( $toggle.hasClass('opened') ) {
			closeToggle($toggle);
		}
	}
	
	/**
	 * @param	{Object} $gaugeContainer
	 * @param	{string} title : gauge title
	 * @param	{float} maxValue : max gauge value
	 */
	function renderGauge($gaugeContainer, title, maxValue) {
		$gaugeContainer.attr('id', 'gauge-' + justGageUniqueId++);
		new JustGage({
			id: $gaugeContainer.attr('id'),
			value: parseFloat($gaugeContainer.attr('data-gauge-value')),
			title: title,
			decimals: 1,
			min: 0,
			max: maxValue,
			gaugeWidthScale: 0.25,
			customSectors: [{
				color: "#ce4844",
				lo: 0,
				hi: 0.89
			},{
				color: "#ffbf00",
				lo: 0.89,
				hi: 0.99
			},{
				color: "#5cb85c",
				lo: 0.99,
				hi: 1000
			}]
		});
	}
	
	function displayComparativeTableForParagraphs($infoMessage) {
		var spintax, oWordsStats, aParagraphsData = [];
		
		// Stats calculation for all paragraphs
		$.each($('textarea[id^=spintax-paragraph-]'), function() {
			spintax = $(this).val().trim(),
			oWordsStats = getWordsStats(spintax),
			aParagraphsData.push({
				variationRate: oWordsStats.variationRate,
				perforationRate: oWordsStats.perforationRate,
				variationIndex: oWordsStats.variationIndex,
				perforationIndex: oWordsStats.perforationIndex,
				qualityIndex: oWordsStats.qualityIndex
			});
		});
		
		// Table building
		$infoMessage.append('' +
			'<div class="grid my-table header">' +
				'<div class="unit one-sixth align-center">' + MySpeech.get("message.paragraph") + '</div>' +
				'<div class="unit one-sixth align-center">' + MySpeech.get("message.replacement_rate") + '</div>' +
				'<div class="unit one-sixth align-center">' + MySpeech.get("message.hole_rate") + '</div>' +
				'<div class="unit one-sixth align-center">' + MySpeech.get("message.replacement_index") + '</div>' +
				'<div class="unit one-sixth align-center">' + MySpeech.get("message.hole_index") + '</div>' +
				'<div class="unit one-sixth align-center">' + MySpeech.get("message.quality_index") + '</div>' +
			'</div>'
		);
		$.each($('textarea[id^=spintax-paragraph-]'), function(i,v) {
			$infoMessage.append('' +
				'<div class="grid my-table row">' +
					'<div class="unit one-sixth align-center">' + parseInt(i+1) +'</div>' +
					'<div class="unit one-sixth align-center">' + ( isNaN(aParagraphsData[i].variationRate) ? "&infin;" : new String(aParagraphsData[i].variationRate).replace('.',MySpeech.get("message.having_seprator_avg")) + '%' ) + '</div>' +
					'<div class="unit one-sixth align-center">' + ( isNaN(aParagraphsData[i].perforationRate) ? "&infin;" : new String(aParagraphsData[i].perforationRate).replace('.',MySpeech.get("message.having_seprator_avg")) + '%' ) + '</div>' +
					'<div class="unit one-sixth align-center">' + ( isNaN(aParagraphsData[i].variationIndex) ? "&infin;" : new String(aParagraphsData[i].variationIndex).replace('.',MySpeech.get("message.having_seprator_avg")) ) + '</div>' +
					'<div class="unit one-sixth align-center">' + ( isNaN(aParagraphsData[i].perforationIndex) ? "&infin;" : new String(aParagraphsData[i].perforationIndex).replace('.',MySpeech.get("message.having_seprator_avg")) ) + '</div>' +
					'<div class="unit one-sixth align-center">' + ( isNaN(aParagraphsData[i].qualityIndex) ? "&infin;" : new String(aParagraphsData[i].qualityIndex).replace('.',MySpeech.get("message.having_seprator_avg")) ) + '</div>' +
				'</div>'
			);
		});
		
		// Marking extreme values in the table
		for ( var i=2; i<=6; i++ ) {
			markExtremeValueIntoTable($('.my-table.row .unit:nth-child(' + i + ')'), 'MIN_VALUE')
			markExtremeValueIntoTable($('.my-table.row .unit:nth-child(' + i + ')'), 'MAX_VALUE')
		}
	}

	/**
	 * @param	{object} $textarea : textarea of the spintax for which the current brackets block displaying should be turned on
	 * @return	none
	 */
	function turnOnCurrentBracketsBlockDisplaying() {
		$.each($('textarea[id^=spintax-paragraph-]'), function(i,v) {
			$(this).removeClass('highlighting-off').addClass('highlighting-on').on('keyup click', displayCurrentBracketsBlock).trigger('keyup');
		});
	}
	
	/**
	 * @param	{object} $textarea : textarea of the spintax for which the current brackets block displaying should be turned off
	 * @return	none
	 */
	function turnOffCurrentBracketsBlockDisplaying() {
		$('textarea[id^=spintax-paragraph-]').removeClass('highlighting-on').addClass('highlighting-off').off('keyup click');
		$('.highlighter-container').html('');
	}
	
	function displayCurrentBracketsBlock(e) {
		var $textarea = $(e.target),
			highlightBeginTag = '<span class="spintax-highlight">{',
			highlightEndTag = '}</span>',
			oIndexes = findIndexesOfCurrentBracketsBlock($textarea.val(), $textarea.prop('selectionStart')),
			$highlighterContainer = $textarea.prev('.highlighter-container'),
			highlighterContainerHtml = $textarea.val().replace(/\n/g, '<br>');
		
		if ( oIndexes.indexOpeningBracket != -1 && oIndexes.indexClosingBracket != -1 ) {
			highlighterContainerHtml = highlighterContainerHtml.replaceCharByString(oIndexes.indexClosingBracket, highlightEndTag); // start by the end tag !
			highlighterContainerHtml = highlighterContainerHtml.replaceCharByString(oIndexes.indexOpeningBracket, highlightBeginTag);
		}
		$highlighterContainer.html(highlighterContainerHtml);
	}
	
	function sortParagraphContainersAlphabetically() {
		$('.paragraph-container').sortElements(function(a, b){
			return $(a).data('title').localeCompare($(b).data('title'));
		});
	}
	
	/**
	 * @param
	 * @return
	 */
	function resizeHighlighterContainersWidth() {
		$.each($('textarea[id^=spintax-paragraph-]'), function(i,v) {
			$(this).prev('.highlighter-container').width($(this).width());
		});
	}
	
	/**
	 * @param	{spintax} string
	 * @param	{integer} errorIndex
	 * @param	{integer} noParagraph
	 * @return	{string} spintax formated
	 */
	function formatSpintaxShownInErrorMessages(spintax, errorIndex, noParagraph, errorarray) {
		var nbCharsAroundErrorIndex = 75;
		var json_msg = errorarray.message;
		
		var flag_punc = json_msg.indexOf(ERROR_MESSAGE.END_PUNCTUTAION_SIGN.message);
		
		var flag_lower_case = json_msg.indexOf(ERROR_MESSAGE.START_LOWER_CASE.message);
		
		var flag_blank = json_msg.indexOf(ERROR_MESSAGE.START_BLANK.message);
		var around_text=spintax.substring(errorIndex - nbCharsAroundErrorIndex, errorIndex);
		
		var around_arr=around_text.split( "\n" );
		
		var around_text_end=spintax.substr(errorIndex + 1, nbCharsAroundErrorIndex);
		
		var around_arr_end=around_text_end.split( "\n" );
		
		//alert(around_arr.length);
		for( var i = 0; i < around_arr.length; ++i ) {
			//alert(around_text);
			//alert(i)
			}
			
		if(around_arr[around_arr.length-1]=="" && around_arr[around_arr.length-1] !='undefined'){
			var text_to_show=around_arr[around_arr.length-2];
			//alert(around_text);
			}else{
				var text_to_show=around_arr[around_arr.length-1];
				}
		
		if(flag_punc > 10){
			return "" +
			
			around_arr[around_arr.length-1] +
			"<a class='spintax-error' href='#' onclick='Spinchecker.selectSpintaxErrorIntoParagraphContent(" + noParagraph + ", " + errorIndex + ")'>" + spintax[errorIndex] + "</a>";
			
			}
			else if(flag_lower_case > 10){
		return "<a class='spintax-error' href='#' onclick='Spinchecker.selectSpintaxErrorIntoParagraphContent(" + noParagraph + ", " + errorIndex + ")'>" + spintax[errorIndex] + "</a>" + 
			around_arr_end[0];
			
			}
			else if(flag_blank > 10){
		return "<a class='spintax-error' href='#' onclick='Spinchecker.selectSpintaxErrorIntoParagraphContent(" + noParagraph + ", " + errorIndex + ")'>" + spintax[errorIndex] + "</a>" + 
			around_arr_end[0];
			
			}
			else{
		return "" +
			around_arr[around_arr.length-1] +
			"<a class='spintax-error' href='#' onclick='Spinchecker.selectSpintaxErrorIntoParagraphContent(" + noParagraph + ", " + errorIndex + ")'>" + spintax[errorIndex] + "</a>" + 
			around_arr_end[0];
			
			}
	}

	/**
	 * @param	{integer} noParagraph
	 * @param	{integer} errorIndex
	 * @return
	 */
	this.selectSpintaxErrorIntoParagraphContent = function(noParagraph, errorIndex) {
		var $paragraphContent =  $('#spintax-paragraph-' + noParagraph);

		openToggleIfClosed( $paragraphContent.parents('.db-toggles-wrapper'));
		scrollToElement($paragraphContent, function() {
			$paragraphContent.focus();
			$paragraphContent.prop('selectionStart', errorIndex).prop('selectionEnd', errorIndex+1);
		});
	}
	
	/**
	 * @deprecated
	 * @param	{integer} noParagraph
	 * @param	{integer} errorIndex
	 * @return
	 */
	this.OLD_selectSpintaxErrorIntoParagraphContent = function(noParagraph, errorIndex) { // déplacer avec les fonctions publiques
		var $paragraphContent =  $('#spintax-paragraph-' + noParagraph),
			oCaretPosition = getCaretCoordinates($paragraphContent.get(0), errorIndex);

		$paragraphContent.focus();
		$('html, body').animate(
			{ scrollTop: oCaretPosition.top }, 
			700, 
			function() { $paragraphContent.prop('selectionStart', errorIndex).prop('selectionEnd', errorIndex); }
		);
	}
		
	/**
	 * @deprecated
	 * @param	{string} spintax
	 * @param	{integer} errorIndex
	 * @return	{string} spintax formated
	 */
	function OLD_formatSpintaxShownInErrorMessages(spintax, errorIndex) {
		return "" +
			buildFadingString(spintax.substring(0, errorIndex), 'IN') + 
			"<span class='spintax-error'>" + spintax[errorIndex] + "</span>" + 
			buildFadingString(spintax.substr(errorIndex + 1), 'OUT');
	}
	
	/**
	 * @deprecated
	 * @param	{string} string
	 * @param	{string} fadingMode : 'IN' / 'OUT'
	 * @return	{string} 
	 */
	function buildFadingString(string, fadingMode) {
		var nbFadingStringBlocks = 5,
			fadingStringBlockSize = 10,
			result = "",
			indexBeginBlock,
			indexEndBlock;
		switch (fadingMode) {
			case 'IN':
				if ( string ) {
					var countBlocks = 1;
					indexEndBlock = string.length;
					while ( indexEndBlock > 0 && countBlocks <= nbFadingStringBlocks ) {
						indexBeginBlock = indexEndBlock - fadingStringBlockSize;
						result = "<span class='fading-in-block-" + countBlocks + "'>" + string.substring(indexBeginBlock, indexEndBlock) + "</span>" + result;
						indexEndBlock -= fadingStringBlockSize;
						countBlocks++;
					}
				}
				break;
			case 'OUT':
				if ( string ) {
					var countBlocks = nbFadingStringBlocks;
					indexBeginBlock = 0;
					while ( indexBeginBlock < string.length && countBlocks ) {
						indexEndBlock = indexBeginBlock + fadingStringBlockSize;
						result = "<span class='fading-out-block-" + countBlocks + "'>" + string.substring(indexBeginBlock, indexEndBlock) + "</span>" + result;
						indexBeginBlock += fadingStringBlockSize;
						countBlocks--;
					}
				}
				break;
			default:
				alert("Function buildFadingString() : ERROR !! Bad fadingMode : " + fadingMode);
		}
		return result;
	}
	
	function getErrorsNature(aErrors) {
		var oResult = { nbWarnings: 0, nbErrors: 0 };
		
		$.each(aErrors, function(i,error) {
			if ( error.type == 'ERROR' ) {
				oResult.nbErrors++;
			}
			if ( error.type == 'WARNING' ) {
				oResult.nbWarnings++;
			}
		});
		
		return oResult;
	}
	
	/** PUBLIC METHODS ***************************************************************************/
	
	/**
	 * @param
	 * @return
	 */
	this.clickOnCheckboxShowCurrentBracketsBlock = function() {
		if ( $('#show-current-brackets-block').is(':checked') ) {
			turnOnCurrentBracketsBlockDisplaying();
		}
		else {
			turnOffCurrentBracketsBlockDisplaying();
		}
	}
	
	this.analyzeArticle = function() {
		$('.loading-block').find('.progress-1, .progress-2').width(0);
        $('.loading-block').addClass('open').delay(400).promise().done(function() {
			var $paragraphContent,
				$paragraphContainer,
				aParagraphsContents,
				noParagraph,
				paragraphTitle,
				isUploadMode = (_this.aUploadedFileNames.length ? true : false );
			
			$('.paragraph-container').remove();

			if(!$('#spintax-article').val().trim()) {
				$('.loading-block').removeClass('open');
				MyUtils.displayInfoMessage('warning', MySpeech.get("message.warning.please_enter_article"));
				$('#spintax-article').val('').focus();
				return;
			}
			
			$('#spintax-article-container').slideUp(400, function() {
				var paragraphCount  = 0;
				aParagraphsContents = $('#spintax-article').val().trim().split('\n\n').reverse();
				
				$.each(aParagraphsContents, function (i,v) {
					noParagraph = aParagraphsContents.length - i;
					paragraphTitle = ( isUploadMode ? 'Fichier ' + _this.aUploadedFileNames[aParagraphsContents.length - i - 1] : 'Paragraphe n° ' + noParagraph );
					$paragraphContent = createParagraphZone(noParagraph, paragraphTitle, v);
					$paragraphContainer = $paragraphContent.parents('.paragraph-container');
					createToggles($paragraphContainer.find('.spintax-paragraph-wrapper'), false);
					createToggles($paragraphContainer.find('.info-message-wrapper'), false);
					$paragraphContent = $('#' + $paragraphContent.prop('id')); // hack after cloning being done in createToggles function
					_this.analyzeParagraph($paragraphContent, false);
					paragraphCount++; if(true === window.debug_spintax) console.log('paragraphCount', paragraphCount);
					$('.loading-block').find('.progress-1').width(Math.ceil(paragraphCount*100/aParagraphsContents.length)+'%')
				});
				
				if(isUploadMode) {
					sortParagraphContainersAlphabetically();
				}
				resizeHighlighterContainersWidth();
				// ParagraphNavigator.fillAndShow($('textarea[id^=spintax-paragraph-]').length);
				$("#detected-paragraph").text(paragraphCount);
				$("#tot_detected_paragraph").val(paragraphCount);
				$("#pr_swap_to").val(paragraphCount);
				$("#btm-options").css('display','block');
				$('.paragraph-container').each(function(i, para_cont) {
					$(para_cont).attr('data-paracontindex', i + 1);
				});
				var total_para = $('#detected-paragraph').html();
				if(total_para == 1){$('#btm-options #rdm').css('display','none');}
				if(total_para > 1) {
					$('.paragraph-container[data-paratype="NORMAL_PARAGRAPH"]').eq(0).find('select[id^="permutation-mode-"]').after('<button type="button" class="apply-permutation-mode-to-all mini">Apply to all</button>');
				}
				//$('.loading-block').removeClass('open');
			});
			$('#show-current-brackets-block-container').slideDown(400);
			
			$('#uploadButton').removeClass('action').addClass('disabled').attr('disabled','disabled');
			//$('#submitButton').html(MySpeech.get("form.button.article_stats")).off('click').on('click', displayArticleStats);
			$('#submitButton').html(MySpeech.get("form.button.create_article")).off('click').on('click', function() {
				$('#no_article').val($('#value-of-x').val());
				getReadbleContent();
			});// OLD: getReadbleContent, NEW: generateTheArticles
			$('#submitButton').addClass('save-art');
			// copied here from DYANCORE.savedata - START
			$("form#db-form").submit(function(e) {
				e.preventDefault();
				$('.loading-block').addClass('open');
				var $this = $(this);
				DYANCORE.process($this, function() {
					if(true === window.debug_spintax) console.log($this.serializeArray());//var formURL = $(this).attr("action");
					$.ajax({
						url: 'create_text_new.php',
						type: 'POST',
						dataType: "html",
						data: $this.serializeArray(),
						success: function(html) {
							$('body').append(html);
							if(html.toLowerCase().indexOf('download') > -1
							&& html.toLowerCase().indexOf('.zip') > -1) {
								$('#playaudio')[0].play();
							}
						}
					});
				});
		   });
		   // copied here from DYANCORE.savedata - END
		});
	}
	
	/**
	 * @param	{object} $paragraphContent
	 * @param	{boolean} openToggleIfErrors : open if closed and scroll to it
	 * @return	
	 */
	this.analyzeParagraph = function($paragraphContent, openToggleIfErrors) { if(true === window.debug_spintax) console.log('%c[analyzeParagraph] - START', 'color:#FC0');
		var spintax = $paragraphContent.val().trim(),
			$paragraphContainer = $paragraphContent.parents('.paragraph-container'),
			aErrors = searchSpintaxErrors(spintax),
			oErrorsNature = getErrorsNature(aErrors),
			noParagraph = $paragraphContent.prop('id').replace('spintax-paragraph-', ''),
			$infoMessageWrapper = $paragraphContainer.find('.info-message-wrapper'),
			$infoMessageErrors = $infoMessageWrapper.find('.info-message'),
			$infoMessageStats = $infoMessageWrapper.next('.info-message'),
			toggleTitle;
			
		$infoMessageErrors.html('').hide();
		$infoMessageStats.html('').hide();
		
		// Paragraph warnings & errors display
		// -----------------------------------
		if ( oErrorsNature.nbErrors || oErrorsNature.nbWarnings ) {
			$infoMessageErrors.html( prepareWarningsErrorsMessage(aErrors, spintax, noParagraph) ).show();
		}
		
		// Paragraph stats display
		// -----------------------
		if ( !oErrorsNature.nbErrors ) {
			$infoMessageStats.html( prepareParagraphStatsMessage($paragraphContent, noParagraph) ).show(function() { 
				renderThreeGauges($infoMessageStats) 
			});
		}
		
		// Toggle title
		// ------------
		if ( !oErrorsNature.nbErrors && !oErrorsNature.nbWarnings ) {
			toggleTitle = MySpeech.get("message.this_paragraph_contains_no_error_no_warning");
		}
		else {
			toggleTitle = MySpeech.get("message.this_paragraph_contains");
			if ( oErrorsNature.nbErrors ) {
				toggleTitle += " <span class='error blink'>" + oErrorsNature.nbErrors + " " + MySpeech.get("message.word_error") + (oErrorsNature.nbErrors > 1 ? "s" : "") + "</span>";
			}
			if ( oErrorsNature.nbWarnings ) {
				toggleTitle += ( oErrorsNature.nbErrors ? " " + MySpeech.get("message.and") + " " : " " ) + "<span class='warning blink'>" + oErrorsNature.nbWarnings + " " + MySpeech.get("message.word_warning") + (oErrorsNature.nbWarnings > 1 ? "s" : "") + "</span>";
			}
		}
		updateToggleTitle($infoMessageWrapper, toggleTitle);
		
		// Toggle closing / opening
		// ------------------------
		if ( !aErrors.length ) {
			closeToggleIfOpened($infoMessageWrapper);
		}
		else if (openToggleIfErrors) {
			openToggleIfClosed($infoMessageWrapper);
		}
		if(true === window.debug_spintax) console.log('%c[analyzeParagraph] - END', 'color:#FC0');
	}
	
	this.init = function() {
		_this.aStopWords = MySpeech.get("variable.stop_words");
		ERROR_MESSAGE.UNNECESSARY_OPENING_BRACKET_OR_MISSING_PIPE.message = MySpeech.get("message.error.unnecessary_opening_bracket_or_missing_pipe");
		ERROR_MESSAGE.UNNECESSARY_CLOSING_BRACKET_OR_MISSING_PIPE.message = MySpeech.get("message.error.unnecessary_closing_bracket_or_missing_pipe");
		
		ERROR_MESSAGE.END_PUNCTUTAION_SIGN.message = MySpeech.get("message.error.end_punctuation_sign");
		
		ERROR_MESSAGE.START_LOWER_CASE.message = MySpeech.get("message.error.start_lower_case");
		
		ERROR_MESSAGE.LINE_NUMBER.message = MySpeech.get("message.error.line_number");
		
		ERROR_MESSAGE.START_BLANK.message = MySpeech.get("message.error.start_blank");
		ERROR_MESSAGE.CONSECUTIVE_WORDS_WITHOUT_VARIATIONS.message = MySpeech.get("message.error.consecutive_words_without_variations_part_1") + " " + _this.NB_MAX_CONSECUTIVE_WORDS_WITHOUT_VARIATIONS + " " + MySpeech.get("message.error.consecutive_words_without_variations_part_2");
		ERROR_MESSAGE.SPINTAX_IS_EMPTY.message = MySpeech.get("message.error.spintax_is_empty");
//		ERROR_MESSAGE.UNNECESSARY_OPENING_BRACKET.message = MySpeech.get("message.error.unnecessary_opening_bracket");
//		ERROR_MESSAGE.UNNECESSARY_CLOSING_BRACKET.message = MySpeech.get("message.error.unnecessary_closing_bracket");
		ERROR_MESSAGE.MISSING_MATCHING_OPENING_BRACKET_FOR_BRACKET.message = MySpeech.get("message.error.missing_matching_opening_bracket_for_bracket");
		ERROR_MESSAGE.MISSING_MATCHING_CLOSING_BRACKET_FOR_BRACKET.message = MySpeech.get("message.error.missing_matching_closing_bracket_for_bracket");
		ERROR_MESSAGE.MISSING_MATCHING_OPENING_BRACKET_FOR_PIPE.message = MySpeech.get("message.error.missing_matching_opening_bracket_for_pipe");
		ERROR_MESSAGE.MISSING_MATCHING_CLOSING_BRACKET_FOR_PIPE.message = MySpeech.get("message.error.missing_matching_closing_bracket_for_pipe");
		
		resetForm();
//		ParagraphNavigator.create();
	}
}

var Spinchecker = new Spinchecker();

/*************************************************************************************************/

function resetForm() {
	hideHelp();
//	ParagraphNavigator.hide();
	Spinchecker.aUploadedFileNames = [];
	$('#default-permutation-mode option').eq(0).prop('selected', true)
	$('#compare-paragraphs').prop('checked', true);
	$('#show-current-brackets-block-container').slideUp(400);
	$('#spintax-article-container').slideDown(400, function() { $('#spintax-article').val('').focus(); } );
	$('.paragraph-container').remove();
	$('#article-stats').remove();
	$('#uploadButton').removeClass('disabled').addClass('action').removeAttr('disabled');
	$('#value-of-x').val(window.value_of_x);
	$('#value-of-x').closest('.unit').show().closest('.grid').find('.unit').removeClass('half').addClass('one-third');
	$('#submitButton').removeClass('disabled').addClass('action').html(MySpeech.get("form.button.article_analysis")).off('click').on('click', function(e) {
		$('#no_article').val($('#value-of-x').val()).attr('readonly', true);
		handle_generate_articles(e, $(this), handle_generate_articles_callback);
	}); /* NEW: handle_generate_articles */ /* OLD: Spinchecker.analyzeArticle */
	$('.radiance-public-message').remove();
	
	$('#btm-options').css('display','none');
}

function handle_generate_articles(e, $context, cb) { if(true === window.debug_spintax) console.log('[handle_generate_articles]');
	e.preventDefault();
	var $this = $context,
		$form = $this.closest('form'),
		$textarea = $form.find('#spintax-article'),
		$no_of_articles = $form.find('#value-of-x'),
		$gen_method = $form.find('[name="gen_method"]'),
		$r_c = $form.find('[name="r_c"]'),
		r_c_value = $r_c.val(),
		$bucket_size = $form.find('[name="bucket_size"]'),
		bucket_size_value = $bucket_size.val(),
		$processes = $form.find('[name="processes"]'),
		$no_of_articles = $form.find('#value-of-x'),
		lang = getCookie('languagename'),
		is_resume_task = false,
		resume_task_url_chunk = window.location.href.match(/\?resume=(.+)/g); // {32}
	if(resume_task_url_chunk !== null
	&& resume_task_url_chunk.length > 0) {
		is_resume_task = resume_task_url_chunk[0].replace('?resume=', '');
	}
	if($gen_method.val() == 'method_2') { if(true === window.debug_spintax) { console.log('r_c_value', r_c_value); console.log('bucket_size_value', bucket_size_value); }
		if(isNaN(r_c_value)
		|| isNaN(bucket_size_value)
		|| bucket_size_value % r_c_value != 0) {
			MyUtils.displayInfoMessage('warning', MySpeech.get("form.label.r_c_not_multiple_of_b_s"));
			return false;
		}
	}
	if($form.hasClass('processing')) {
		return false;
	}
	$form.addClass('processing');
	$.ajax({
		url: false === is_resume_task ? 'upload-input.php' : 'resume-task.php',
		data: {
			spintax_input: $textarea.val(),
			no_of_articles: $no_of_articles.val(),
			gen_method: $gen_method.val(),
			r_c: $r_c.val(),
			bucket_size: $bucket_size.val(),
			processes: $processes.val(),
			nonce: (new Date()).getTime(),
			resume_task: is_resume_task
		},
		dataType: 'json',
		method: 'POST',
		context: $form
	}).done(function(response) {
		if(true === window.debug_spintax) console.log(response);
		/* Moved to `ensure_generation_completed`
		MyUtils.displayInfoMessage('success', MySpeech.get("form.label.spintax_uploaded"));*/
		handle_generate_articles_before_callback(response);
		if(typeof cb == 'function') {
			cb(response);
		}
	}).fail(function(error) {
		if($gen_method.val() == 'method_2') {
			$form.addClass('checking-status');
			$.ajax({
				url: 'get-uploads-dir-list.php',
				dataType: 'json',
				method: 'GET',
				context: $form
			}).done(function(response) {
				if(typeof response.upload_dirs != 'undefined'
				&& response.upload_dirs.length == 1
				&& typeof response.upload_dirs[0] != 'undefined'
				&& response.upload_dirs[0].length == 32) {
					let prepared_response = {
						uid: response.upload_dirs[0],
						parallel: true,
						hashed: input_is_hashed($textarea.val())
					};
					handle_generate_articles_before_callback(prepared_response);
					if(typeof cb == 'function') {
						cb(prepared_response);
					}
				} else {
					console.error('Request failed! Status:', error.status, ' JSON:', error.responseJSON, ' RAW:', error.responseText);
					MyUtils.displayInfoMessage('warning', typeof error.responseJSON == 'undefined' || error.responseJSON.message == 'undefined' ? 'A fatal error has occurred' : error.responseJSON.message);
				}
			});
		} else {
			console.error('Request failed! Status:', error.status, ' JSON:', error.responseJSON, ' RAW:', error.responseText);
			MyUtils.displayInfoMessage('warning', typeof error.responseJSON == 'undefined' || error.responseJSON.message == 'undefined' ? 'A fatal error has occurred' : error.responseJSON.message);
		}
	}).always(function() {
		if(!$form.hasClass('checking-status'))
			$form.removeClass('processing');
	});
}

function handle_generate_articles_before_callback(response) { if(true === window.debug_spintax) console.log('[handle_generate_articles_before_callback]');
	if($('#export-format').length == 0) {
		$('#value-of-x').closest('.unit').hide().after(
			'<div class="unit one-third">'
				+'<label for="export-format" data-speech-key="form.label.export_format">'+MySpeech.get("form.label.export_format")+'</label>'
				+'<select name="export_format" id="export-format">'
					+'<option value="text">Text (ZIP)</option>'
					+(typeof response.hashed != 'undefined' && response.hashed == true ? '<option value="json" selected="">JSON</option>' : '')
				+'</select>'
			+'</div>'
		); //.closest('.grid').find('.unit').removeClass('one-third').addClass('half');
	}
	if(typeof response.uid != 'undefined') {
		$('[name="folder"]').val(response.uid);
		if(true === window.debug_spintax && false) { // Disabled, as this is not much needed
			window.open('uploads/'+response.uid+'/variations-report.json');
		}
	}
}

let total_task_procs_count,
	scaling_status_label = '',
	scaling_sub_status_label = '',
	cluster_scaling_check_interval,
	k8s_scaling_check_interval,
	scale_the_cluster = function(scale_direction, cb) {
		scale_direction = scale_direction === 'out' ? scale_direction : 'in';
		$('body').addClass('scaling-the-cluster').attr('data-scalingcluster', scale_direction);
		let required_nodes = scale_direction === 'out' ? Math.ceil(total_task_procs_count / window.cluster_pods_per_node) : 0; // NaN error July 20 4:20pm when resuming task
		if(true === window.debug_spintax) console.log('[scale_the_cluster] '+(scale_direction === 'out' ? 'Scaling cluster to '+required_nodes+' nodes to run '+total_task_procs_count+' parallel processes' : 'Scaling back to '+required_nodes+' nodes'));
		$('.cluster-scaling-status .status').html('Scaling '+scale_direction+'...');
		$('.cluster-scaling-status .sub-status').html(scale_direction === 'out' ? 'The cluster needs '+required_nodes+' node'+(required_nodes == 1 ? '' : 's')+' to run '+total_task_procs_count+' parallel process'+(total_task_procs_count == 1 ? '' : 'es') : 'Scaling back to zero nodes');
		$.ajax({
			url: 'cluster-scale-'+scale_direction+'.php',
			data: {
				required_nodes: required_nodes
			},
			dataType: 'json',
			method: 'POST'
		}).done(function(response) {
			if(true === window.debug_spintax) console.log(response);
			if(true === response.cluster_pool_update_required
			|| scale_direction === 'in') {
				cluster_scaling_check_interval = setInterval(function() {
					check_cluster_status(scale_direction, required_nodes, cb);
				}, 1000*60*1);
			} else {
				check_cluster_status(scale_direction, required_nodes, cb);
			}
		});
	},
	check_cluster_status = function(scale_direction, required_nodes, cb) {
		if(true === window.debug_spintax) console.log('[check_cluster_status]');
		$.ajax({
			url: 'cluster-status.php',
			data: {
				required_nodes: required_nodes
			},
			dataType: 'json',
			method: 'POST'
		}).done(function(response) {
			if(true === window.debug_spintax) console.log(response);
			if(response.status_pool == 'ready'
			&& response.status_nodes == 'ready') {
				clearInterval(cluster_scaling_check_interval);
				if(scale_direction === 'out') {
					scale_k8s(scale_direction, function() {
						$('body').addClass('cluster-scaled-out');
						handle_check_cluster_status(cb);
					});
				} else {
					handle_check_cluster_status(cb);
				}
			}
		});
	},
	handle_check_cluster_status = function(cb) {
		if(true === window.debug_spintax) console.log('[handle_check_cluster_status]');
		$('.cluster-scaling-status .status').html('Scaling complete').delay(3000).promise().done(function() {
			$('body').removeClass('scaling-the-cluster').removeAttr('data-scalingcluster');
			if(typeof cb == 'function')
				cb();
		});
	},
	scale_k8s = function(scale_direction, cb) {
		scale_direction = scale_direction === 'out' ? scale_direction : 'in';
		$('body').addClass('scaling-the-cluster').attr('data-scalingcluster', scale_direction);
		let required_pods = scale_direction === 'out' ? total_task_procs_count : 0;
		if(true === window.debug_spintax) console.log('[scale_k8s] '+(scale_direction === 'out' ? 'Scaling K8s to '+required_pods+' pods' : 'Scaling K8s to zero pods'));
		$('.cluster-scaling-status .status').html('Scaling '+scale_direction+'...');
		$('.cluster-scaling-status .sub-status').html(scale_direction === 'out' ? 'The cluster needs '+required_pods+' pod'+(required_pods == 1 ? '' : 's') : 'Scaling back to zero pods');
		$.ajax({
			url: 'cluster-scale-k8s.php',
			data: {
				required_pods: required_pods
			},
			dataType: 'json',
			method: 'POST'
		}).done(function(response) {
			if(true === window.debug_spintax) console.log(response);
			if(typeof response.success != 'undefined')
				$('form#db-form').find('#user_options_processes').val(required_pods);
			k8s_scaling_check_interval = setInterval(function() {
				check_k8s_status(scale_direction, required_pods, cb);
			}, 1000*60*1);
		});
	},
	check_k8s_status = function(scale_direction, required_pods, cb) {
		if(true === window.debug_spintax) console.log('[check_k8s_status]');
		$.ajax({
			url: 'cluster-k8s-status.php',
			data: {
				required_pods: required_pods
			},
			dataType: 'json',
			method: 'POST'
		}).done(function(response) {
			if(true === window.debug_spintax) console.log(response);
			if(response.status == 'ready') {
				clearInterval(k8s_scaling_check_interval);
				if(scale_direction == 'in') {
					scale_the_cluster(scale_direction, cb);
				} else {
					if(typeof cb == 'function')
						cb();
				}
			}
		});
	};

function display_processing_popup(show) {
	show = typeof show == 'undefined' ? true : show;
	let $form = $('form#db-form');
	if($form.find('#processing-status-display').length == 0) {
		$form.append(
			'<div id="processing-status-display">'
				+'<div class="progress-bar" data-label="Processing..."><span></span></div>'
				+'<a class="upload-folder-link" href="generation-display.php?hash='+$form.find('[name="folder"]').val()+'" target="_blank">'+MySpeech.get("form.label.click_to_view_processing_folder")+'</a>'
				+'<ul class="workers"></ul>'
				+('cluster' === window.env ?
				'<div class="cluster-scaling-status">'
					+'<span class="status"></span>'
					+'<span class="sub-status"></span>'
				+'</div>' : '')
			+'</div>'
		);
	}
	if(show == true)
		$form.addClass('checking-status processing show-processing');
	else
		$form.removeClass('checking-status show-processing');
}

function handle_generate_articles_callback(response) { if(true === window.debug_spintax) console.log('[handle_generate_articles_callback]');
	if(true === window.parallel
	&& typeof response.parallel != 'undefined'
	&& true === response.parallel) {
		// init remote workers
		if('cluster' == window.env) {
			total_task_procs_count = response.pending_tasks_count;
			display_processing_popup(true);
			scale_the_cluster('out', function() {
				init_remote_workers($('form#db-form'), function() {
					Spinchecker.analyzeArticle();
				});
			});
		} else {
			init_remote_workers($('form#db-form'), function() {
				Spinchecker.analyzeArticle();
			});
		}
		/*// parallel processing needs checking DB to check if all processes have finished working
		ensure_generation_completed($('form#db-form'), function() {
			Spinchecker.analyzeArticle();
		});*/
	} else {
		// linear processing does not use DB and status check is not needed
		let lang = getCookie('languagename');
		MyUtils.displayInfoMessage('success', MySpeech.get("form.label.spintax_uploaded"));
		Spinchecker.analyzeArticle();
	}
}

function init_remote_workers($form, cb) { if(true === window.debug_spintax) console.log('[init_remote_workers]');
	var uid = $form.find('[name="folder"]').val(),
		$no_of_articles = $form.find('#value-of-x'),
		lang = getCookie('languagename'),
		worker_status = function(cb_worker_status) { if(true === window.debug_spintax) console.log('[worker_status]');
			$.ajax({
				url: 'worker-status.php',
				data: {
					uid: uid
				},
				dataType: 'json',
				method: 'POST',
				context: $form
			}).done(function(response) {
				if(true === window.debug_spintax) console.log(response);
				cb_worker_status(response);
			});
		},
		handle_worker_status = function(response) { if(true === window.debug_spintax) console.log('[handle_worker_status]');
			let pending_procs = response.pending_procs,
				idle_workers = response.idle_workers,
				$processes = $form.find('[name="processes"]'),
				workers_to_init = Math.min(idle_workers.length, pending_procs.length, parseInt($processes.val())),
				idle_worker_index = 0,
				idle_worker_interval;
			if(workers_to_init > 0) {
				idle_worker_interval = setInterval(function() {
					if(idle_worker_index < idle_workers.length
					&& idle_worker_index < pending_procs.length) {
						if(true === window.debug_spintax) console.log('Start new worker... #'+(idle_worker_index + 1));
						start_new_worker(idle_workers[idle_worker_index], pending_procs[idle_worker_index]);
					} else {
						clearInterval(idle_worker_interval);
						if(true === window.debug_spintax) console.log('Wait '+window.proc_worker_status_check_every_x_min+' min, then trigger `worker_status`');
						setTimeout(function() {
							worker_status(handle_worker_status);
						}, 1000*60*window.proc_worker_status_check_every_x_min);
					}
					idle_worker_index++;
				}, 1000*window.proc_worker_launch_every_x_sec);
			} else {
				if(true === window.debug_spintax) console.log('No workers to init');
				// Check if all workers have finished working
				let workers_count = response.workers.length,
					idle_workers_count = 0;
				$.each(response.workers, function(i, worker) {
					if(worker.status == 'idle')
						idle_workers_count++;
				});
				if(workers_count == idle_workers_count) {
					if(true === window.debug_spintax) console.log('All workers appear to have finished processing');
					$('body').delay(2000).promise().done(function() {
						let handle_no_workers_to_init = function() {
							$form.removeClass('show-processing').delay(2000).promise().done(function() {
								ensure_generation_completed($form, function() {
									Spinchecker.analyzeArticle();
								});
							});
						};
						if('cluster' == window.env) {
							scale_k8s('in', handle_no_workers_to_init);
						} else {
							handle_no_workers_to_init();
						}
					});
				} else {
					if(true === window.debug_spintax) console.log((workers_count - idle_workers_count)+' of '+workers_count+' appear to be processing their tasks');
					if(true === window.debug_spintax) console.log('Wait '+window.proc_worker_status_check_every_x_min+' min, then trigger `worker_status`');
					setTimeout(function() {
						worker_status(handle_worker_status);
					}, 1000*60*window.proc_worker_status_check_every_x_min);
				}
			}
			render_worker_status(response);
		},
		render_worker_status = function(response) { if(true === window.debug_spintax) console.log('[render_worker_status]');
			display_processing_popup(true);
			let $processing_display = $form.addClass('show-processing').find('#processing-status-display'),
				$workers = $processing_display.find('ul.workers');
			$processing_display.find('.progress-bar span').width((response.total_worked * 100 / response.total_workable)+'%');
			$workers.empty();
			for(let i = 0; i < response.workers.length; i++) {
				$workers.append(
					'<li data-workerid="'+response.workers[i].id+'" class="'+response.workers[i].status+'">'
						+'<span class="wrap">'
							+'<span class="title">Worker #'+(i + 1)+'</span>'
							+'<span class="assigned">'+(response.workers[i].assigned == null ? '' : '#'+response.workers[i].assigned)+'</span>'
							+'<span class="status">'+response.workers[i].status+'</span>'
							+'<span class="action">'+(response.workers[i].pid == null ? '' : 'PID: #'+response.workers[i].pid)+'</span>'
						+'</span>'
					+'</li>'
				);
			}
		},
		start_new_worker = function(worker, proc) { if(true === window.debug_spintax) console.log('[start_new_worker]', proc);
			let $worker = $('li[data-workerid="'+worker.id+'"]');
			$worker.addClass('starting').find('.status').html('starting');
			$.ajax({
				url: 'worker-start.php',
				data: {
					uid: uid,
					worker_id: worker.id,
					proc_id: proc.id
				},
				dataType: 'json',
				method: 'POST',
				context: $form
			}).done(function(response) {
				if(true === window.debug_spintax) console.log(response);
				handle_start_new_worker(worker, proc, response);
			});
		},
		handle_start_new_worker = function(worker, proc, response) { if(true === window.debug_spintax) console.log('[handle_start_new_worker]');
			let $worker = $('li[data-workerid="'+worker.id+'"]');
			if(typeof response.worker_status != 'undefined'
			&& typeof response.running_confirmed != 'undefined'
			&& response.running_confirmed == true) {
				let pid_label = 'running' == response.worker_status.status && response.worker_status.pid ? 'PID: #'+response.worker_status.pid : '';
				$worker.find('.assigned').html(null != response.worker_status.assigned ? '#'+response.worker_status.assigned : '');
				$worker.attr('class', response.worker_status.status).find('.status').html(response.worker_status.status);
				$worker.find('.action').html(pid_label);
			} else {
				$worker.attr('class', '').find('.status').html('failed').delay(3000).promise().done(function() { $worker.find('.status').html('idle'); });
			}
		};
	$form.addClass('processing checking-status');
	worker_status(handle_worker_status);
}

function ensure_generation_completed($form, cb) {
	var uid = $form.find('[name="folder"]').val(),
		$no_of_articles = $form.find('#value-of-x'),
		lang = getCookie('languagename');
	$form.addClass('processing checking-status');
	$.ajax({
		url: 'check-gen-status.php',
		data: {
			uid: uid
		},
		dataType: 'json',
		method: 'POST',
		context: $form
	}).done(function(response) {
		if(true === window.debug_spintax) console.log(response);
		switch(response.status) {
			case 'error':
				MyUtils.displayInfoMessage('warning', 'There was a problem checking the status of variant generation.');
				$form.removeClass('checking-status');
			break;
			case 'complete':
				if(typeof response.duration != 'undefined') {
					display_generation_duration($form, response.duration);
				}
				MyUtils.displayInfoMessage('success', MySpeech.get("form.label.spintax_uploaded"));
				$form.removeClass('checking-status');
				if(typeof cb == 'function') {
					cb();
				}
			break;
			case 'running':
			default:
				if(typeof response.total != 'undefined'
				&& typeof response.complete != 'undefined') {
					$('form#db-form').attr('data-proctotal', response.total).attr('data-proccomplete', response.complete);
				}
				$('body').delay(5000).promise().done(function() {
					ensure_generation_completed($form, cb);
				});
			break;
		}
	}).fail(function(error) {
		console.log(error.responseJSON, error.status);
		MyUtils.displayInfoMessage('warning', typeof error.responseJSON.message == 'undefined' ? 'A fatal error has occurred when checking the generation status' : error.responseJSON.message);
	}).always(function() {
		if(!$form.hasClass('checking-status'))
			$form.removeClass('processing');
	});
}

function display_generation_duration($form, dur) {
	$form.find('.grid.head').after('<div class="gen-duration-display" />');
	let duration = [];
	if(dur.d > 0) {
		dur.h += dur.d * 24;
	}
	if(dur.h > 0) {
		duration.push(dur.h+MySpeech.get("form.label.hours"));
	}
	duration.push(Math.max(1, dur.m + Math.ceil(dur.s / 60))+MySpeech.get("form.label.minutes"));
	$form.find('.gen-duration-display').html(MySpeech.get("form.label.all_var_gen_in")+duration.join(' '));
}

function input_is_hashed(str) {
	return str.indexOf('#start-') > -1
		&& str.split('#start-').length == str.split('#end-').length;
}

function showHelp() {
	$('.info-message[class~=help]').slideUp(400, function() {
		$(this).find('.help-content').html( MySpeech.get("application.help").join("") );
		$(this).find('span#reference-variation-rate').html(Spinchecker.REFERENCE_RATE.VARIATION * 100);
		$(this).find('span#reference-perforation-rate').html(Spinchecker.REFERENCE_RATE.PERFORATION * 100);
		$(this).find('span#max-consecutive-words-without-variations').html(Spinchecker.NB_MAX_CONSECUTIVE_WORDS_WITHOUT_VARIATIONS);
		$(this).find('div#stop-words-list').html(Spinchecker.aStopWords.sort().join(', '));
		//$(this).find('.close-button a').html("<i class='fa fa-fw fa-chevron-up'></i> " + MySpeech.get("hide_help", true)).off('click').on('click', hideHelp);
		$(this).find('.close-button a').html("<i class='fa fa-fw fa-chevron-up'>Show help</i>");
		//$(this).slideDown(400);
	});
}

function hideHelp() {
	$('.info-message[class~=help]').slideUp(400, function() {
		$(this).find('.help-content').html('');
		$(this).find('.close-button a').html("<i class='fa fa-fw fa-chevron-down'></i> " + MySpeech.get("show_help", true)).off('click').on('click', showHelp);
		$(this).slideDown(400);
	});
}

function addThousandsSeparator(input) {
    var output = input
    if (parseFloat(input)) {
        input = new String(input); // so you can perform string operations
        var parts = input.split("."); // remove the decimal part
        parts[0] = parts[0].split("").reverse().join("").replace(/(\d{3})(?!$)/g, "$1,").split("").reverse().join("");
        output = parts.join(".");
    }
    return output;
}
    
function genRandomOption(nmParagraph) {
	var detectedElementCount = $("#detected-elements-"+nmParagraph).text();
	var PermutationMode  = $("#permutation-mode-"+nmParagraph).val(); 
	$("input[name='cnt_par["+nmParagraph+"][rand_from]']").val(1);
	$("input[name='cnt_par["+nmParagraph+"][rand_fr]']").val(parseInt(detectedElementCount));
	$("input[name='cnt_par["+nmParagraph+"][rand_to]']").val(parseInt(detectedElementCount));
	$("input[name='cnt_par["+nmParagraph+"][rand_t]']").val(parseInt(detectedElementCount));
	$("#random-opt-area-"+nmParagraph).find("#btm-error").html('');
	if(PermutationMode == 'ALL_PERMUTABLE')
	{
		$("input[name='cnt_par["+nmParagraph+"][rand_from]']").val(parseInt(detectedElementCount) );
		$("input[name='cnt_par["+nmParagraph+"][rand_fr]']").val(1);;
		$("input[name='cnt_par["+nmParagraph+"][rand_to]']").val(parseInt(detectedElementCount) );
		$("input[name='cnt_par["+nmParagraph+"][rand_t]']").val(parseInt(detectedElementCount) );
		//$("input[name='cnt_par["+nmParagraph+"][rand_from]']").val(1);
		//$("input[name='cnt_par["+nmParagraph+"][rand_fr]']").val(1);
		//$("input[name='cnt_par["+nmParagraph+"][rand_to]']").val(parseInt(detectedElementCount));
		//$("input[name='cnt_par["+nmParagraph+"][rand_t]']").val(parseInt(detectedElementCount));
	}
	else if(PermutationMode == 'ALL_PERMUTABLE_EXCEPT_FIRST')
	{
		$("input[name='cnt_par["+nmParagraph+"][rand_from]']").val(parseInt(detectedElementCount) );
		$("input[name='cnt_par["+nmParagraph+"][rand_fr]']").val(1);
		$("input[name='cnt_par["+nmParagraph+"][rand_to]']").val(parseInt(detectedElementCount) );
		$("input[name='cnt_par["+nmParagraph+"][rand_t]']").val(parseInt(detectedElementCount) );
		//$("input[name='cnt_par["+nmParagraph+"][rand_from]']").val(2);
		//$("input[name='cnt_par["+nmParagraph+"][rand_fr]']").val(2);
		//$("input[name='cnt_par["+nmParagraph+"][rand_to]']").val(parseInt(detectedElementCount));
		//$("input[name='cnt_par["+nmParagraph+"][rand_t]']").val(parseInt(detectedElementCount));
	}
	else if(PermutationMode == 'ALL_PERMUTABLE_EXCEPT_LAST')
	{
		$("input[name='cnt_par["+nmParagraph+"][rand_from]']").val(parseInt(detectedElementCount) );
		$("input[name='cnt_par["+nmParagraph+"][rand_fr]']").val(1);
		$("input[name='cnt_par["+nmParagraph+"][rand_to]']").val(parseInt(detectedElementCount) );
		$("input[name='cnt_par["+nmParagraph+"][rand_t]']").val(parseInt(detectedElementCount) );
		//$("input[name='cnt_par["+nmParagraph+"][rand_from]']").val(2);
		//$("input[name='cnt_par["+nmParagraph+"][rand_fr]']").val(2);
		//$("input[name='cnt_par["+nmParagraph+"][rand_to]']").val(parseInt(detectedElementCount));
		//$("input[name='cnt_par["+nmParagraph+"][rand_t]']").val(parseInt(detectedElementCount));
	}
	else if(PermutationMode == 'ALL_PERMUTABLE_EXCEPT_FIRST_LAST')
	{
		$("input[name='cnt_par["+nmParagraph+"][rand_from]']").val(parseInt(detectedElementCount) );
		$("input[name='cnt_par["+nmParagraph+"][rand_fr]']").val(1);
		$("input[name='cnt_par["+nmParagraph+"][rand_to]']").val(parseInt(detectedElementCount) );
		$("input[name='cnt_par["+nmParagraph+"][rand_t]']").val(parseInt(detectedElementCount) );
		//$("input[name='cnt_par["+nmParagraph+"][rand_from]']").val(3);
		//$("input[name='cnt_par["+nmParagraph+"][rand_fr]']").val(3);
		//$("input[name='cnt_par["+nmParagraph+"][rand_to]']").val(parseInt(detectedElementCount) );
		//$("input[name='cnt_par["+nmParagraph+"][rand_t]']").val(parseInt(detectedElementCount) );
	}else if(PermutationMode == 'ALL_NOT_PERMUTABLE')
	{
		$("input[name='cnt_par["+nmParagraph+"][rand_from]']").val(parseInt(detectedElementCount) );
		$("input[name='cnt_par["+nmParagraph+"][rand_fr]']").val(1);
		$("input[name='cnt_par["+nmParagraph+"][rand_to]']").val(parseInt(detectedElementCount) );
		$("input[name='cnt_par["+nmParagraph+"][rand_t]']").val(parseInt(detectedElementCount) );
	}
		var rand_from = $("input[name='cnt_par["+nmParagraph+"][rand_from]']").val();
		var rand_fr = $("input[name='cnt_par["+nmParagraph+"][rand_fr]']").val();
		var rand_to = $("input[name='cnt_par["+nmParagraph+"][rand_to]']").val();
		var rand_t = $("input[name='cnt_par["+nmParagraph+"][rand_t]']").val();
	if(rand_from>rand_to){	rand_from = rand_to;	}   
	if(rand_fr>rand_t){	rand_fr = rand_t;	}   
		var rand_from = $("input[name='cnt_par["+nmParagraph+"][rand_from]']").val(rand_from);
		var rand_fr = $("input[name='cnt_par["+nmParagraph+"][rand_fr]']").val(rand_fr);
		var rand_to = $("input[name='cnt_par["+nmParagraph+"][rand_to]']").val(rand_to);
		var rand_t = $("input[name='cnt_par["+nmParagraph+"][rand_t]']").val(rand_t);
		
	$('#random-opt-area-'+nmParagraph).css('display', 'block');
	
}    
function change_para_swap_box(nmbParagraph) {
	var intro 		= 0;
	var concl 		= 0;
	var total_para  = 0;
	$('.para_rand_val').each(function(){
		var val = $(this).val();
		if(val=='INTRO_PARAGRAPHP'){intro= intro+1; }
		if(val=='CONCLUSION_PARAGRAPH'){concl= concl+1; }
		total_para= total_para+1;
		});
	var first_box	=	total_para;
	var second_box	=	total_para;
		if(intro >= 1 && concl >= 1) {
			first_box = 3;
			second_box = total_para-(intro+concl-2);
		} else if (intro >= 1) {
			first_box = 2;
			second_box = total_para-(intro-1);
		} else if(concl >= 1) {
			first_box = 2;
			second_box = total_para-(concl-1);
		}
	if(first_box > second_box) {
		first_box = second_box;
	}
	$("input[name='pr_swap_from']").val(first_box);
	$("input[name='pr_swap_to']").val(second_box);
	$("input[name='pr_swap_from_hide']").val(first_box);
	$("input[name='pr_swap_to_hide']").val(second_box);
}

(function($) {

	$(document).ready(function() {

		$('body').on('click', '.apply-permutation-mode-to-all', function(e) {
			e.preventDefault();
			let $this = $(this),
				$para_container = $this.closest('.paragraph-container');
			$para_container.siblings('.paragraph-container[data-paratype="NORMAL_PARAGRAPH"]').each(function(i, para_cont) {
				let elementcount = $(para_cont).find('span[id^="detected-elements-"]').html() || 1;
				elementcount = parseInt(elementcount);
				if(elementcount > 1) {
					$(para_cont).find('select[name*="[permutation_mode]"]').val($para_container.find('select[name*="[permutation_mode]"]').val());
				}
			})
		});

		$('#resume-task button.resume').click(function(e) {
			handle_generate_articles(e, $(this), handle_generate_articles_callback);/*
			let prepared_response = {
				uid: $('#pseudo-uid').val(),
				parallel: true,
				hashed: input_is_hashed($('textarea#spintax-article').val())
			};
			$('form#db-form').addClass('processing');
			handle_generate_articles_before_callback(prepared_response);
			handle_generate_articles_callback(prepared_response);*/
		});

	});

}(jQuery));