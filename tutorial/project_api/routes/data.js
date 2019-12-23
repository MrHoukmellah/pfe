var express = require('express');
var router = express.Router();
var elasticsearch = require('elasticsearch');
var client = new elasticsearch.Client({  
  host: 'localhost:9200'
 });

router.post('/', function(req, res, next) {
  var ids = req.body._id;
  client.search({
    index: 'products',
    type: 'item',
    size: 50,
    body: {
        "query": {
            "terms": {
                "_id": ids
            }
        }
        
    }
  }).then(function(ids) {
      res.json(ids.hits.hits);
  })
});

module.exports = router;