var express = require('express');
var router = express.Router();
var elasticsearch = require('elasticsearch');
var client = new elasticsearch.Client({  
  host: 'localhost:9200'
 });

router.get('/', function(req, res, next) {
  // var limit = req.query.limit || 20;
  // var offset = req.query.offset || 0;

  client.search({
    index: 'products',
    type: 'item',
    size: 50,
    scroll: '60m',
    body: {
      "query": {
        "match_all": {}
      }
    }
  }).then(function(response) {
      res.json({"products": response.hits.hits, "scrollId": response._scroll_id});
  })
});
router.post('/infiniteScrollSearch', function(req, res){
  console.log('scroll Id =>', req.body.scrollId);
  scrollId = req.body.scrollId;

  client.scroll(
    {
      scrollId: scrollId,
      scroll: '60m'
    }).then( function(response) {
      console.log("response scroll =>", response);
      res.json({"products": response.hits.hits, "scrollId": response._scroll_id});
    })
})
router.post('/', function(req, res, next) {
  var q = req.body.q;
  client.search({
    index: 'products',
    type: 'item',
    size: 50,
    scroll: '60m',
    body: {
      "query": {
        "multi_match" : {
          "query": q, 
          "fields": [ "title", "description", "brand" ],        }
      }
        
    }
  }).then(function(response) {
      res.json({"products": response.hits.hits, "scrollId": response._scroll_id});
  })
});

module.exports = router;
