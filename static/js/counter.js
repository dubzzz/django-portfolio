function format_counter(counter_value_) {
	var ext = '';
	var counter_value = counter_value_;
	if (counter_value >= 500000000) {
		ext = 'B';
		counter_value /= 1000000000.0;
	} else if (counter_value >= 500000) {
		ext = 'M';
		counter_value /= 1000000.0;
	} else if (counter_value >= 500) {
		ext = 'k';
		counter_value /= 1000.0;
	}

	if (counter_value >= 10 || counter_value_ < 10)
		return parseInt(counter_value);
	else	
		return parseInt(counter_value) + '.' + (parseInt(counter_value * 10) %10) + ext;
}

function run_counters() {
	var done = true;
	$("[data-counter]").each(function() {
		var counter_max = this.getAttribute("data-counter");
		var current_counter_value_str = this.getAttribute("data-counter-value");
		
		var current_counter_value = 0;
		if (current_counter_value_str)
			current_counter_value = parseInt(current_counter_value_str)
		
		var next_counter_value = current_counter_value;
		if (current_counter_value < 10)
			next_counter_value++;
		else
			next_counter_value = Math.floor(1.2 * current_counter_value);
		
		if (next_counter_value <= counter_max) {
			done = false;
			$(this).html(format_counter(next_counter_value));
			this.setAttribute("data-counter-value", next_counter_value);
		} else if (current_counter_value <= counter_max) {
			$(this).html(format_counter(counter_max));
			this.setAttribute("data-counter-value", next_counter_value);
		}
	});

	if (!done) {
		setTimeout(run_counters, 75);
	}
}

