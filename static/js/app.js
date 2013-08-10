$(function(){
  // get from the server the current number of tweets
  function update_count(){
    $.ajax('/count').done(function(data){
      $('#tweets').text(data.count)
    })
  }
  // get every five seconds
  setInterval(update_count, 5000)
})

$(function(){
  // The SVG container
  var width  = 960,
      height = 550;

  var projection = d3.geo.mercator()
                  .translate([480, 300])
                  .scale(970);

  var path = d3.geo.path()
      .projection(projection);

  var svg = d3.select("#map").append("svg")
      .attr("width", width)
      .attr("height", height);

  var tooltip = d3.select("#map").append("div")
      .attr("class", "tooltip");

  queue()
      .defer(d3.json, "static/maps/world-110m.json")
      .defer(d3.tsv, "static/maps/world-country-names.tsv")
      // as long as it's json, you can grab dynamic content too :O
      .defer(d3.json, "view/geo?group_level=1&stale=ok")
      .await(ready);

  function ready(error, world, names, counts_rows) {

    var countries = topojson.object(world, world.objects.countries).geometries,
        neighbors = topojson.neighbors(world, countries),
        i = -1,
        n = countries.length,
        counts = {},
        most = Math.max.apply(null, counts_rows.rows.map(function(row){ 
          return row.value
        })),
        color = d3.scale.log().domain([1, most]).range(['black', 'blue']);

    counts_rows.rows.forEach(function(count){
      counts[count.key[0]] = count.value
    })

    countries.forEach(function(d) { 
      var filtered_names = names.filter(function(n) { return d.id == n.id })
      if(filtered_names.length) d.name = filtered_names[0].name

      if(counts[d.name]) {
        d.count = counts[d.name]
      }
    });

  var country = svg.selectAll(".country").data(countries);

    country
     .enter()
      .insert("path")
      .attr("class", "country")    
        .attr("title", function(d,i) { return d.name; })
        .attr("d", path)
        .style("fill", function(d, i) { 
          return color(d.count); 
        })

    //Show/hide tooltip
    country
      .on("mousemove", function(d,i) {
        var mouse = d3.mouse(svg.node()).map( function(d) { return parseInt(d); } )

        tooltip
          .classed("hidden", false)
          .attr("style", "left:"+(mouse[0]+25)+"px;top:"+mouse[1]+"px")
          .html(d.name + ", " + (d.count || "0") + " tweets")
      })
      .on("mouseout",  function(d,i) {
        tooltip.classed("hidden", true)
      });

  
  var legend = svg
    .append("g")
    .attr("class", "legend")
    .attr("x", width - 65)
    .attr("y", 25)
    .attr("height", 100)
    .attr("width", 100)

  legend
    .selectAll("g")
    .data([most, 1])
    .enter()
    .append("g")
    .each(function(d, i){
      var g = d3.select(this)
      g.append("rect")
        .attr("x", width - 90)
        .attr("y", height - (i * 25) - 16)
        .attr("height",10)
        .attr("width",10)
        .style("fill", color(d))

      var legend_item = g.append("text")
        .attr("x", width - 75)
        .attr("y", height - (i * 25) - 8)
        .attr("height",30)
        .attr("width",100)
        .text(String(d) + " tweets")
        .style("fill", color(d))
    })
    .append("text")
    .attr("x", width - 90)
    .attr("y", height - 48)
    .attr("height",10)
    .attr("width",10)
    .style("font-size", "16px") 
    .style("text-decoration", "underline") 
    .text("Legend")
  }
})