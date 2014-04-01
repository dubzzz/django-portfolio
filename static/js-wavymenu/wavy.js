
function scrollToAnchor(aid){
	var aTag = $(aid);
	$('html,body').animate({scrollTop: aTag.offset().top},'slow');
}

/*
 * Move the wavy menu up or down
 * CALLED BY: scroll and resize on $(window)
 */
var OFFSET_LEFT_MENU_ITEMS = 10;
var OFFSET_TOP_MENU_ITEMS = 10;
var IS_SOFT_MOVE_REQUIRED = ! (navigator.userAgent.search("Firefox") > -1);
function alignMenuItems(content, menu_items, soft_move) {
	menu_items.style.left = (content.offsetLeft + content.clientWidth - menu_items.clientWidth + OFFSET_LEFT_MENU_ITEMS) + "px";
	if (IS_SOFT_MOVE_REQUIRED && soft_move) {
		$(menu_items).stop();

		if ($(window).scrollTop() <= content.offsetTop)
			$(menu_items).animate({opacity: .4, top: (content.offsetTop + OFFSET_TOP_MENU_ITEMS) + "px"}, 250);
		else
			$(menu_items).animate({opacity: .4, top: ($(window).scrollTop() + OFFSET_TOP_MENU_ITEMS) + "px"}, 250);
	} else { // due to discontinuous display on Chrome / 'else' works perfectly with Firefox
		if ($(window).scrollTop() <= content.offsetTop)
			menu_items.style.top = (content.offsetTop + OFFSET_TOP_MENU_ITEMS) + "px";
		else
			menu_items.style.top = ($(window).scrollTop() + OFFSET_TOP_MENU_ITEMS) + "px";
	}
}

/*
 * Create a wavy menu for content
 *
 * @params:
 * 	content: block which contains the details concerning the menu
 * 	menu_items: wavy menu
 *	imgClassDependent: add an image next to the name of the menu if required, [{className: "className", imgSrc:"imgSrc"}]
 */
var id_ = 0;
function createWavyMenu(content_, menu_items_, imgClassDependent) {
	// Generate the menu
	content_.find("[data-anchor]").each(function() {
		// Generate an id for the element iff it does not have any id
		if (! this.getAttribute("id")) {
			this.setAttribute("id", "auto-generated-id-" + (id_++));
		}
		// Add an image if necessary
		for (var i=0 ; i!=imgClassDependent.length ; i++) {
			if ($(this).hasClass(imgClassDependent[i].className)) {
				menu_items_.append("<li onclick=\"scrollToAnchor('#" + this.getAttribute("id") + "');\"><img src=\"" + imgClassDependent[i].imgSrc + "\" /> " + this.getAttribute("data-anchor") + "</li>");
				return;
			}
		}
		// No image
		menu_items_.append("<li onclick=\"scrollToAnchor('#" + this.getAttribute("id") + "');\">" + this.getAttribute("data-anchor") + "</li>");
	});

	// OnMouseOver for menu-items's li
	menu_items_.find("li").hover(function() {
		menu_items_.stop();
		menu_items_.fadeTo(250, 1.);
	},
	function() {
		menu_items_.stop();
		menu_items_.fadeTo(1000, .4);
	});
	
	// Initialise triggers
	var content = content_[0];
	var menu_items = menu_items_[0];
	menu_items_.fadeTo(3000, .4);
	alignMenuItems(content, menu_items, false);
	$(window).scroll(function() {alignMenuItems(content, menu_items, true);});
	$(window).resize(function() {alignMenuItems(content, menu_items, false);});
}

