// var select_button = window.frames[0].document.getElementById('o1181952181');
// var value_input = window.frames["ifm"].document.getElementsByName('stakeTxt_0');
// var place_bet_btn = window.frames["ifm"].document.getElementById('placeBetBtn');

// select_button.click()
// value_input.value = '5';
// place_bet_btn.click()

var select_button = window.frames['MainFrame'].document.getElementById('%s');

var value_input;
var place_bet_btn;

select_button.click();

setTimeout(function(){
    value_input = window.frames['NavigatorFrame'].document.getElementById('stakeTxt_0');
    place_bet_btn = window.frames['NavigatorFrame'].document.getElementById('placeBetBtn'); 
    value_input.value = '%s';
    place_bet_btn.click();
},1000)
