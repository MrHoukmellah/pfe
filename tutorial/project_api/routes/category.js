var express = require('express');
var router = express.Router();
var elasticsearch = require('elasticsearch');
var client = new elasticsearch.Client({  
  host: 'localhost:9200'
 });

router.post('/', function(req, res, next) {
    var q  = req.body.q;
    var category = req.body.category;
    client.search({
        index: 'products',
        type: 'item',
        size: 50,
        body: {
            query: {
                bool : {
                    "must":{
                        "multi_match" : {
                            "query": q,
                            "fields": [ "title", "description" ]
                        }
                    },
                    "filter": [
                        { "match_phrase": { "category": category } }
                    ],        
                }
            }
        }
    }).then(function(q) {
        res.json(q.hits.hits);
    })
});

module.exports = router;