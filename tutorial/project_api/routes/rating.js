var express = require('express');
var router = express.Router();
var elasticsearch = require('elasticsearch');
var client = new elasticsearch.Client({  
  host: 'localhost:9200'
 });

 router.post('/', function(req, res, next) {
  var category = req.body.category;
  client.search({
      index: 'products',
      type: 'item',
      scroll: '60m',
      size: 50,
      body: {
          query: {
              
                  "match" : {
                      "category": category,
                  }

          }
      }
  }).then(function(category) {
      res.json({'products': category.hits.hits, "scrollId": category._scroll_id});
  })
});


module.exports = router;
