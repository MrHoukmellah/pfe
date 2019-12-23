var express = require('express');
var router = express.Router();
var elasticsearch = require('elasticsearch');
var client = new elasticsearch.Client({  
  host: 'localhost:9200'
 });

router.post('/', function(req, res, next) {
  var title = req.body.title;
  client.search({
    index: 'products',
    type: 'item',
    size: 50,
    body: {
        query: {
            match: {
                title: title
            }
        }
        
    }
  }).then(function(title) {
      res.json(title.hits.hits);
  })
});

module.exports = router;