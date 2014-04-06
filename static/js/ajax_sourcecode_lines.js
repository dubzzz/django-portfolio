function ajax_sourcecode_lines(element_id, url, attempts=60) {
	if (attempts <= 0)
		return;

	$.ajax({
		type: "GET",
		url: url,
		dataType: "xml",
		success: function(xml) {
			try_again = true;
			$(xml).find('lines').each(function() {
				try_again = false;
				$("#" + element_id).append($("<li>", {text: $(this).text()}));
			});
			if (try_again) {
				setTimeout(ajax_sourcecode_lines, 5000, element_id, url, attempts -1);
			}
		}
	});
}

