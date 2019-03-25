// Event listener for hour slider
$('#timeSlider').on('input', function() {
	// Get current date and time from HTML elements for request
	var currDate = new Date($('#dateText')[0].textContent),
		hours = $('#timeSlider')[0].valueAsNumber;
	currDate.setHours(hours);
	
	// Set display date and time
	$( "#dateText" ).text(formatDateDisplay(currDate));
	
	// Display loading spinner while request is sent and hide results
	$('#spinner-div').css('display', 'inline');
	$('#model-results').css('display', 'none');	
	
	// Reset selected node and edge styling
	d3.select('#nodes').selectAll('.selected-airport').attr('r', 3);
	d3.select('#nodes').selectAll('.selected-airport').classed('selected-airport', false);
	d3.select('#edges').selectAll('.selected-flight-path').each(function(d) {
		d3.select(this).classed('selected-flight-path', false);
		d3.select(this).style({
			'stroke-opacity': opacityScale(Number(d.od_cancel_ratio)),
			'stroke': colorScale(Number(d.od_cancel_ratio))
		});
		d3.select(this).attr('marker-end', arrow(colorScale(Number(d.od_cancel_ratio)), opacityScale(Number(d.od_cancel_ratio))));
	});
	
	// Reset origin and destination airport text
	$('#origin-airport-id').text('Select an airport from the map below:');
	$('#origin-airport-res').text('');
	$('#origin-airport-loc').text('');
	$('#dest-airport-id').text('Select an airport from the map below:');
	$('#dest-airport-res').text('');
	$('#dest-airport-loc').text('');
	origin = true;
	airportsSelected = false;

	
	// Gather both responses and wait for finish, need airport lookup for network data
	var airportsResponse = $.getJSON('/api/airports-url-parameters', {
		datetime: formatDateAjax(currDate),
	});
	var networkResponse = $.getJSON('/api/network-url-parameters', {
		datetime: formatDateAjax(currDate),
	});
	$.when(airportsResponse, networkResponse).done(
		function(airports, network) { 
			updateAirports(airports[0]); 
			updateNetwork(network[0]); 
		}
	);
	
	// Gather both responses and wait for finish
	var classifyResponse = $.getJSON('/api/classify-url-parameters', {
		datetime: formatDateAjax(currDate),
		origin: origin_id,
		dest: dest_id,
	});
	var regResponse = $.getJSON('/api/reg-url-parameters', {
		datetime: formatDateAjax(currDate),
		origin: origin_id,
		dest: dest_id,
	});
	$.when(classifyResponse, regResponse).done(
		function(classify, reg) {
			updateModelResults(classify[0], reg[0], airportsSelected);	
		}
	);
});

// Helper function for date format for Ajax request
function formatDateAjax(date) {
  return date.getFullYear() + '-' + (date.getMonth() + 1) + '-' + date.getDate() + ' ' + date.getHours() + ':' + date.getMinutes() + ':' + date.getSeconds();
}

// Helper function for date format for display text
function formatDateDisplay(date) {
  var monthNames = [
    "January", "February", "March",
    "April", "May", "June", "July",
    "August", "September", "October",
    "November", "December"
  ];

  var day = date.getDate();
  var monthIndex = date.getMonth();
  var year = date.getFullYear();
  var hour = date.getHours();
  
  var amPM = hour >= 12 ? 'PM' : 'AM';
  hour = hour > 12 ? hour - 12 : hour;
  
  day = day < 10 ? '0' + day : day;
  hour = hour < 10 ? '0' + hour : hour;
  
  hour = hour === '00' ? 12 : hour;

  return monthNames[monthIndex] + ' ' + day + ', ' + year + ' ' + hour + ':00 ' + amPM;
}

// Initiate datepicker, set to autoclose on selection
$('.date-picker').datepicker({
	autoclose: true
});

// Event listener for date selector
$('.date-picker').on('changeDate', function(ev) {
	// Gather the current date and time from HTML elements
	var currDate = new Date($('#dateText')[0].textContent),
		newDate = new Date($('.date-picker').val());
	currDate.setFullYear(newDate.getFullYear());
	currDate.setMonth(newDate.getMonth());
	currDate.setDate(newDate.getDate());
	
	// Set date time text
	$( "#dateText" ).text(formatDateDisplay(currDate));
	
	// Display loading spinner and remove model results section
	$('#spinner-div').css('display', 'inline');
	$("#model-results").css("display", "none");
	
	// Reset selected node and edge styling
	d3.select('#nodes').selectAll('.selected-airport').attr('r', 3);
	d3.select('#nodes').selectAll('.selected-airport').classed('selected-airport', false);
	d3.select('#edges').selectAll('.selected-flight-path').each(function(d) {
		d3.select(this).classed('selected-flight-path', false);
		d3.select(this).style({
			'stroke-opacity': opacityScale(Number(d.od_cancel_ratio)),
			'stroke': colorScale(Number(d.od_cancel_ratio))
		});
		d3.select(this).attr('marker-end', arrow(colorScale(Number(d.od_cancel_ratio)), opacityScale(Number(d.od_cancel_ratio))));
	});
	
	// Reset origin and destination airport text
	$('#origin-airport-id').text('Select an airport from the map below:');
	$('#origin-airport-res').text('');
	$('#origin-airport-loc').text('');
	$('#dest-airport-id').text('Select an airport from the map below:');
	$('#dest-airport-res').text('');
	$('#dest-airport-loc').text('');
	origin = true;
	airportsSelected = false;
	
	// Gather both responses and wait for finish, need airport lookup for network data
	var airportsResponse = $.getJSON('/api/airports-url-parameters', {
		datetime: formatDateAjax(currDate),
	});
	var networkResponse = $.getJSON('/api/network-url-parameters', {
		datetime: formatDateAjax(currDate),
	});
	$.when(airportsResponse, networkResponse).done(
		function(airports, network) { 
			updateAirports(airports[0]); 
			updateNetwork(network[0]); 
		}
	);
	
	// Gather both responses and wait for finish
	var classifyResponse = $.getJSON('/api/classify-url-parameters', {
		datetime: formatDateAjax(currDate),
		origin: origin_id,
		dest: dest_id,
	});

	var regResponse = $.getJSON('/api/reg-url-parameters', {
		datetime: formatDateAjax(currDate),
		origin: origin_id,
		dest: dest_id,
	});
	$.when(classifyResponse, regResponse).done(
		function(classify, reg) {
			updateModelResults(classify[0], reg[0], airportsSelected);	
		}
	);
});

// Set width and height based on window
var width = window.innerWidth,
	height = 500;

// Initialize explainability section variables
var explainWidth, explainHeight, explainMargins, explainScales, classifySVG, regSVG, classifyY, barHeight, featureTexts,
	padding = 25;

// Set map loading overlay height and width
$('#map-container').css('height', height);
$('#map-container').css('width', width);

// Define d3 projection
var projection = albersUsaPr()
	.translate([width / 2, height / 2])
	.scale([1000]);
	
// Define path
var path = d3.geo.path()
	.projection(projection);

// Define flight path color scale
var colorScale = d3.scale.sqrt()
	.domain([0, 1])
	.range(['green', 'red']);

// Define opacity scale for flights - lighter for flights with low likelihood of cancellation
var opacityScale = d3.scale.sqrt()
	.domain([0, 1])
	.range([0.2, 1]);

// Define width scale for flights - thinner for flights with low likelihood of cancellation
var widthScale = d3.scale.sqrt()
	.domain([0, 1])
	.range([1, 3]);

// Define color scale for on-time arrow - medium gray-to-green scale
var onTimeScale = d3.scale.pow().exponent(3)
	.domain([0, 1])
	.range(["#AAAAAA","#009933"]);

// Define color scale for delay arrow - medium gray-to-yellow scale
var delayScale = d3.scale.sqrt()
	.domain([0, 1])
	.range(["#AAAAAA","#ffcc00"]);
	
// Define SVG
var svg = d3.select('#us-map-div')
	.append('svg')
	.attr('width', width)
	.attr('height', height);

// Set up airport tooltip
var div = d3.select("body").append("div")   
    .attr("class", "tooltip")               
    .style("opacity", 0);

// Set up arrowhead markers for lines
function arrow(color, opacity) {
	svg.append("svg:defs").append("svg:marker")
		.attr('id', color.replace('#',''))
		.attr('viewBox', "0 -5 10 10")
		.attr('refX', 20)
		.attr('refY', 0)
		.attr('markerWidth', 6)
		.attr('markerHeight', 6)
		.attr('orient', 'auto')
		.attr('markerUnits', 'userSpaceOnUse')
		.style('fill', color)
		.style('fill-opacity', Math.min(1, opacity * 2))
		.append('svg:path')
		.attr('d', 'M0,-5L10,0L0,5');
	return 'url('+color+')';
}

// Load JSON data
d3.queue()
	.defer(d3.json, '/static/data/us_states.json')
	.defer(d3.json, '/static/data/feature_descriptions.json')
	.await(ready);

// Boolean for origin and dest selector on click
var origin = true;

// Boolean for airports selected
var airportsSelected = false;

// Airport lat/long lookup, updates on each update for airports data, used for flight paths based on airport ids
var airportLookup = {};

// Global vars to hold origin and destination ids
var origin_id = 11433,
	dest_id = 12953;

// Global var to check if this is first time displaying explainability section: if so, append svg, if not, ignore
var explainFirst = false;

// Display states when json loaded
function ready(err, us_states, feature_descriptions) {
	if (err) { throw err; }
	
	// Initialize feature texts
	featureTexts = feature_descriptions;
	
	// Append states data
	var states = svg.append('g')
		.selectAll('path')
		.data(us_states.features)
		.enter().append('path')
		.attr('d', path)
		.style('stroke', '#000000')
		.style('stroke-width', '1px')
		.style('fill', '#ffffff');
		
	// Apply top level groups so airports (nodes) display on top of flights (edges)
	svg.append('g').attr('id', 'edges');
	svg.append('g').attr('id', 'nodes');
}


// Get default date/time and default UI display
var currDate = new Date($('#dateText')[0].textContent),
	hours = $('#timeSlider')[0].valueAsNumber;
currDate.setHours(hours);

// Set date time text
$( "#dateText" ).text(formatDateDisplay(currDate));

// Display loading spinner
$('#spinner-div').css('display', 'inline');

// Gather both responses and wait for finish, need airport lookup for network data
var airportsResponse = $.getJSON('/api/airports-url-parameters', {
	datetime: formatDateAjax(currDate),
});
var networkResponse = $.getJSON('/api/network-url-parameters', {
	datetime: formatDateAjax(currDate),
});
$.when(airportsResponse, networkResponse).done(
	function(airports, network) {
		updateAirports(airports[0]); 
		updateNetwork(network[0]); 
	}
);

// Gather both responses and wait for finish
var classifyResponse = $.getJSON('/api/classify-url-parameters', {
	datetime: formatDateAjax(currDate),
	origin: origin_id,
	dest: dest_id,
});
var regResponse = $.getJSON('/api/reg-url-parameters', {
	datetime: formatDateAjax(currDate),
	origin: origin_id,
	dest: dest_id,
});
$.when(classifyResponse, regResponse).done(
	function(classify, reg) {
		updateModelResults(classify[0], reg[0], airportsSelected);	
	}
);

// Function to display model results
// TODO: find a better way to access ::before and ::after elements to color arrows: currently appending new style elements each time
function updateModelResults(classify, reg, flag) {
	if (flag) {
		// Get rid of loading spinner and display model results section below map
		$('#spinner-div').css('display', 'none');
		$("#model-results").css("display", "inline");
		
		// If no data from flight
		if (classify.data === null || reg.data === null) {
			$("#explainability-section").css("display", "none");
			
			// Set model results to default text
			$("#cancel-text").text("No data for this date, time, and airport combination. Please select a date, time, and pair of airports with existing flights.");	
			$("#on-time-text").text("No data for this date, time, and airport combination");	
			$("#delay-text").text("No data for this date, time, and airport combination");	
			$("#reg-text").text("No data for this date, time, and airport combination");
			
			// Reset colors to default grey
			$("#on-time-text").css("background-color", "#AAAAAA");
			$("#delay-text").css("background-color", "#AAAAAA");
			
			// Setting color of CSS elements that make arrows
			var style = document.head.appendChild(document.createElement('style'));
			style.innerHTML = "#on-time-text::before { border-color: #AAAAAA transparent; } " +
							  "#on-time-text::after { border-color: transparent #AAAAAA; } " +
							  "#delay-text::before { border-color: #AAAAAA transparent; } " +
							  "#delay-text::after { border-color: transparent #AAAAAA; } ";
		}
		else {
			// Set model results text
			$("#cancel-text").text(displayPercentage(classify.data.prediction.cancelled) + " chance of cancellation");	
			$("#on-time-text").text(displayPercentage(classify.data.prediction['on-time']) + " chance of on-time flight");	
			$("#delay-text").text(displayPercentage(classify.data.prediction.delayed) + " chance of delay");	
			$("#reg-text").text("If flight is delayed, expect a delay of " + displayDelay(reg.data.prediction));	
			
			// Get colors based on color scale
			onTimeColor = onTimeScale(classify.data.prediction['on-time']);
			delayColor = delayScale(classify.data.prediction.delayed);
			
			// Set arrow colors
			$("#on-time-text").css("background-color", onTimeColor);
			$("#delay-text").css("background-color", delayColor);
			
			// Setting color of CSS elements that make arrows
			var style = document.head.appendChild(document.createElement('style'));
			style.innerHTML = "#on-time-text::before { border-color: " + onTimeColor + " transparent; } " +
							  "#on-time-text::after { border-color: transparent " + onTimeColor + "; } " +
							  "#delay-text::before { border-color: " + delayColor + " transparent; } " +
							  "#delay-text::after { border-color: transparent " + delayColor + "; } ";
			
			// Display explainability section
			$("#explainability-section").css("display", "inline");
			
			if (!explainFirst) {
				// Margins, height, width, and scales for explainability graphs
				explainMargins = {top: 25, bottom: 25, right: 25, left: 110};
				explainWidth = document.getElementById('classify-model-container').clientWidth - explainMargins.left - explainMargins.right;
				explainHeight = 500 - explainMargins.top - explainMargins.bottom;
				explainScales = {x: null, y: null};

				// Define classification explainability SVG
				classifySVG = d3.select('#classify-graph')
					.append('svg')
					.attr('width', explainWidth + explainMargins.left + explainMargins.right)
					.attr('height', explainHeight + explainMargins.top + 3 * explainMargins.bottom)
					.append('g')
					.attr('transform', 'translate(' + explainMargins.left + ', ' + explainMargins.top + ')');

				// Define regression explainability SVG
				regSVG = d3.select('#reg-graph')
					.append('svg')
					.attr('width', explainWidth + explainMargins.left + explainMargins.right)
					.attr('height', explainHeight + explainMargins.top + 3 * explainMargins.bottom)
					.append('g')
					.attr('transform', 'translate(' + explainMargins.left + ', ' + explainMargins.top + ')');
				
				// Set up scales for explainability section
				explainScales.x = d3.scale.linear()
					.domain([0, 1])
					.range([0, explainWidth]);
				explainScales.y = d3.scale.ordinal()
					.domain(['od_pair_delay', 'od_cancel_ratio', 'airport_out_delay', 'airport_cancel_ratio'])
					.rangeBands([explainHeight, 0]);
				
				// Create Y axis and append to existing SVG
				yAxis = d3.svg.axis()
					.scale(explainScales.y)
					.orient('left');
				classifySVG.append('g')
					.attr('class', 'axis')
					.style('font', '10px sans-serif')
					.call(yAxis);
				regSVG.append('g')
					.attr('class', 'axis')
					.style('font', '10px sans-serif')
					.call(yAxis);

				// Add explanation mouseover to labels
				classifySVG.selectAll('.tick')
					.on("mouseover", function(d) {
					// Display tooltip over label
					div.transition()        
						.duration(200)      
						.style("opacity", .9);      
					div.html("<strong>" + featureTexts[d].title + "</strong>" + "<br/>" + featureTexts[d].description)  
						.style("left", (d3.event.pageX) + "px")     
						.style("top", (d3.event.pageY - 28) + "px");    
					})                  
					.on("mouseout", function(d) {       
						// Rremove tooltip over point
						div.transition()        
							.duration(200)      
							.style("opacity", 0);   
					});
				
				// Add explanation mouseover to labels
				regSVG.selectAll('.tick')
					.on("mouseover", function(d) {
					// Display tooltip over label
					div.transition()        
						.duration(200)      
						.style("opacity", .9);      
					div.html("<strong>" + featureTexts[d].title + "</strong>" + "<br/>" + featureTexts[d].description)  
						.style("left", (d3.event.pageX) + "px")     
						.style("top", (d3.event.pageY - 28) + "px");    
					})                  
					.on("mouseout", function(d) {       
						// Rremove tooltip over point
						div.transition()        
							.duration(200)      
							.style("opacity", 0);   
					});
				
				// Set height of explainability bars
				barHeight = explainScales.y.rangeBand() - 2 * padding;
				
				// Set boolean flag now that svgs are appended to DOM
				explainFirst = true;
			}
			
			// Reshape data so it's easier to append to d3 rectangles
			var classifyDataReshaped = [
				{
					attr: 'od_pair_delay',
					val: classify.data['feature_importance']['od_pair_delay'],
					raw: classify.data['feature_values']['od_pair_delay'],
				},
				{
					attr: 'od_cancel_ratio',
					val: classify.data['feature_importance']['od_cancel_ratio'],
					raw: classify.data['feature_values']['od_cancel_ratio'],
				},
				{
					attr: 'airport_out_delay',
					val: classify.data['feature_importance']['airport_out_delay'],
					raw: classify.data['feature_values']['airport_out_delay'],
				},
				{
					attr: 'airport_cancel_ratio',
					val: classify.data['feature_importance']['airport_cancel_ratio'],
					raw: classify.data['feature_values']['airport_cancel_ratio'],
				}
			];
			var regDataReshaped = [
				{
					attr: 'od_pair_delay',
					val: reg.data['feature_importance']['od_pair_delay'],
					raw: reg.data['feature_values']['od_pair_delay'],
				},
				{
					attr: 'od_cancel_ratio',
					val: reg.data['feature_importance']['od_cancel_ratio'],
					raw: reg.data['feature_values']['od_cancel_ratio'],
				},
				{
					attr: 'airport_out_delay',
					val: reg.data['feature_importance']['airport_out_delay'],
					raw: reg.data['feature_values']['airport_out_delay'],
				},
				{
					attr: 'airport_cancel_ratio',
					val: reg.data['feature_importance']['airport_cancel_ratio'],
					raw: reg.data['feature_values']['airport_cancel_ratio'],
				}
			];
			
			// Enter
			var classifyRects = classifySVG.selectAll('.bar')
				.data(classifyDataReshaped);
			
			// Update
			classifyRects.enter().append('rect')
				.attr('class', 'bar');
			
			classifyRects.attr('x', 0)
				.attr('y', function(d) { return padding + explainScales.y(d.attr); })
				.attr('height', barHeight)
				.attr('width', function(d) { return explainScales.x(d.val); })
				.on("mouseover", function(d) {
					// Display tooltip over point
					div.transition()        
						.duration(200)      
						.style("opacity", .9);      
					div.html("<strong>" + featureTexts[d.attr].title + ' : ' + displayFeature(d.raw, d.attr) + "</strong>" + "<br/>" + featureTexts[d.attr].description)  
						.style("left", (d3.event.pageX) + "px")     
						.style("top", (d3.event.pageY - 28) + "px");    
				})                  
				.on("mouseout", function(d) {       
					// Rremove tooltip over point
					div.transition()        
						.duration(200)      
						.style("opacity", 0);   
				});
				
			// Exit
			classifyRects.exit().remove();
			
			// Enter for Text
			var classifyText = classifySVG.selectAll('.bar-text')
				.data(classifyDataReshaped);
			
			// Update for Text
			classifyText.enter().append('text')
				.attr('class', 'bar-text');
			
			classifyText.text(function(d) { return displayPercentage(d.val); })
				.attr('x', function(d) { return 5 + explainScales.x(d.val);})
				.attr('y', function(d) { return 3 + (padding + explainScales.y(d.attr)) + (barHeight / 2); });
			
			// Exit for Text
			classifyText.exit().remove();
			
			// Enter
			var regRects = regSVG.selectAll('.bar')
				.data(regDataReshaped);
			
			// Update
			regRects.enter().append('rect')
				.attr('class', 'bar');
			
			regRects.attr('x', 0)
				.attr('y', function(d) { return padding + explainScales.y(d.attr); })
				.attr('height', barHeight)
				.attr('width', function(d) { return explainScales.x(d.val); })
				.on("mouseover", function(d) {
					// Display tooltip over point
					div.transition()        
						.duration(200)      
						.style("opacity", .9);      
					div.html("<strong>" + featureTexts[d.attr].title+ ' : ' + displayFeature(d.raw, d.attr) + "</strong>" + "<br/>" + featureTexts[d.attr].description)  
						.style("left", (d3.event.pageX) + "px")     
						.style("top", (d3.event.pageY - 28) + "px");    
				})                  
				.on("mouseout", function(d) {       
					// Remove tooltip over point
					div.transition()        
						.duration(200)      
						.style("opacity", 0);   
				});
			
			// Exit
			regRects.exit().remove();
			
			// Enter for Text
			var regText = regSVG.selectAll('.bar-text')
				.data(regDataReshaped);
			
			// Update for Text
			regText.enter().append('text')
				.attr('class', 'bar-text');
			
			regText.text(function(d) { return displayPercentage(d.val); })
				.attr('x', function(d) { return 5 + explainScales.x(d.val);})
				.attr('y', function(d) { return 3 + (padding + explainScales.y(d.attr)) + (barHeight / 2); });
			
			// Exit for Text
			regText.exit().remove();
		}
		// Scroll down to new model results section
		window.scrollTo(0,$('#model-results')[0].offsetTop);
	}
}


// Function to display airports data
function updateAirports(airports) {
	// Get rid of loading spinner
	$('#spinner-div').css('display', 'none');
	
	// Enter
	var airportCircles = svg.select('#nodes').selectAll('.airport-circle')
		.data(airports.data.airports);
	
	// Update
	airportCircles.enter().append('circle')
		.attr('class', 'airport-circle');
	airportCircles.attr('r', 3)
		.each(function(d) {
			var p = projection([d.longitude, d.latitude]);
			airportLookup[d.airport_id] = p;
			if (p) {
				d3.select(this).attr({
					cx: p[0],
					cy: p[1]
				});
			}
		})
		.on("mouseover", function(d) {
			// Display tooltip over point
            div.transition()        
                .duration(200)      
                .style("opacity", .9);      
            div.html("<strong>" + d.airport_name + "</strong>" + "<br/>" + d.airport_city_name)  
                .style("left", (d3.event.pageX) + "px")     
                .style("top", (d3.event.pageY - 28) + "px");    
            })                  
        .on("mouseout", function(d) {       
			// Remove tooltip over point
            div.transition()        
                .duration(200)      
                .style("opacity", 0);   
        })
		.on("click", function(d) {
			// Treat origin and destination differently
			if (origin) {
				// Reset selected node and edge styling
				d3.select('#nodes').selectAll('.selected-airport').attr('r', 3);
				d3.select('#nodes').selectAll('.selected-airport').classed('selected-airport', false);
				d3.select('#edges').selectAll('.selected-flight-path').each(function(d) {
					d3.select(this).classed('selected-flight-path', false);
					d3.select(this).style({
						'stroke-opacity': opacityScale(Number(d.od_cancel_ratio)),
						'stroke': colorScale(Number(d.od_cancel_ratio))
					});
					d3.select(this).attr('marker-end', arrow(colorScale(Number(d.od_cancel_ratio)), opacityScale(Number(d.od_cancel_ratio))));
				})
				
				// Set origin airport text
				$('#origin-airport-id').text(d.airport_name);
				$('#origin-airport-res').text(d.airport_name);
				$('#origin-airport-loc').text(d.airport_city_name);
				
				// Reset destination airport text
				$('#dest-airport-id').text('Select an airport from the map below:');
				$('#dest-airport-res').text('');
				$('#dest-airport-loc').text('');
				
				// Remove model results if they are currently displayed
				$("#model-results").css("display", "none");
				
				// Style newly selected node
				d3.select(this).classed('selected-airport', true);
				d3.select(this).attr('r', 5);
				
				// Set helper global variables, 
				origin = !origin;
				origin_id = d.airport_id;
				airportsSelected = false;
			}
			else {
				// Set global variable for selected airports
				airportsSelected = true;
				
				// Set destination airport text
				$('#dest-airport-id').text(d.airport_name);
				$('#dest-airport-res').text(d.airport_name);
				$('#dest-airport-loc').text(d.airport_city_name);
				
				// Set helper global variables
				origin = !origin;
				dest_id = d.airport_id
				
				// Style newly selected node
				d3.select(this).classed('selected-airport', true);
				d3.select(this).attr('r', 5);
				
				// Style edge between newly selected nodes
				d3.select('#edges').selectAll('.flight-path').each(function(e) {
					if (e.origin_id === origin_id && e.dest_id === dest_id) {
						d3.select(this).classed('selected-flight-path', true);
						d3.select(this).attr('marker-end', arrow('#3071A9', 1.0));
						d3.select(this).style('stroke-opacity', 1.0);
						d3.select(this).style('stroke', '#3071A9');
					}
				});
				
				// Get current selected date and time for requests
				var currDate = new Date($('#dateText')[0].textContent),
					hours = $('#timeSlider')[0].valueAsNumber;
				currDate.setHours(hours);
				
				// Display loading spinner while requests are being made
				$('#spinner-div').css('display', 'inline');
				
				// Gather both responses and wait for finish
				var classifyResponse = $.getJSON('/api/classify-url-parameters', {
					datetime: formatDateAjax(currDate),
					origin: origin_id,
					dest: dest_id,
				});
				var regResponse = $.getJSON('/api/reg-url-parameters', {
					datetime: formatDateAjax(currDate),
					origin: origin_id,
					dest: dest_id,
				});
				$.when(classifyResponse, regResponse).done(
					function(classify, reg) {
						updateModelResults(classify[0], reg[0], true);	
					}
				);
			}
		});
	
	// Exit
	airportCircles.exit().remove();
}

// Function to display network state
function updateNetwork(networkData) {
	// Enter
	var flightPaths = svg.select('#edges').selectAll('.flight-path')
		.data(networkData.data.network);
	
	// Update
	flightPaths.enter().append('line')
		.attr('class', 'flight-path');
	flightPaths.each(function(d) {
			if (airportLookup[d.origin_id] && airportLookup[d.dest_id]) {
				// Style flight path by cancel ratio
				d3.select(this).attr({
					x1: airportLookup[d.origin_id][0],
					y1: airportLookup[d.origin_id][1],
					x2: airportLookup[d.dest_id][0],
					y2: airportLookup[d.dest_id][1],
					"marker-end": arrow(colorScale(Number(d.od_cancel_ratio)), opacityScale(Number(d.od_cancel_ratio)))
				});
				d3.select(this).style('stroke', colorScale(Number(d.od_cancel_ratio)));
				d3.select(this).style('stroke-opacity', opacityScale(Number(d.od_cancel_ratio)));
			}
		});
	
	// Exit
	flightPaths.exit().remove();
}

// Helper function to display percentage from decimal value
function displayPercentage(val) {
	return (val*100).toFixed(2) + '%';	
}

// Helper function to display delay time
function displayDelay(val) {
	var hours = Math.floor(val / 60);
	var minutes = Math.floor(val % 60);
	minutes = minutes >= 10 ? minutes : '0' + minutes
	return hours + ":" + minutes;
}

// Helper function to display raw feature values
function displayFeature(val, feature) {
	if (feature === 'airport_cancel_ratio' || feature === 'airport_cancel_ratio') {
		return displayPercentage(Number(val).toFixed(2));
	}
	else {
		return Math.round(Number(val)) + 'min';	
	}
}
