function run_counters() {
	var done = true;
	$("[data-counter]").each(function() {
		var counter_max = this.getAttribute("data-counter");
		var counter_value = parseInt(this.innerHTML) +1;
		if (counter_value <= counter_max) {
			done = false;
			$(this).html(counter_value);
		}
	});

	if (!done) {
		setTimeout(run_counters, 100);
	}
}

