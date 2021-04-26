import json
from math import ceil
from odoo.http import Controller, route, request
from pprint import pprint

SORT_KEY_MAP = dict([('name', 'name.raw'),
                     ('price', 'calculated_price')])
SORTING_DIRECTION = ('asc', 'desc')


def get_sort_keys(s, d):
    sort_keys, sort_dir = [], d and d.lower()
    for s_key in s.split(','):
        if s_key in SORT_KEY_MAP:
            s_key = SORT_KEY_MAP.get(s_key, s_key)
            sort_keys.append({s_key: sort_dir} if sort_dir in SORTING_DIRECTION else s_key)
    return sort_keys


class OnlifeSearchAPI(Controller):

    @route('/api/product/search', type='http', methods=['GET'], auth='none', csrf=False)
    def product_fuzzy_search(self, keyword=None, brandId=None, brandName=None, limit=20, page=0,
                             sort=None, direction=None):
        product_index = request.env['es.index'].sudo().search([('model_id.model', '=', 'product.template')], limit=1)

        params = request.params

        try:
            offset = int(page) * int(limit)
        except ValueError:
            offset = 0

        try:
            max_ = float(params.get('max'))
        except (ValueError, TypeError):
            max_ = None

        try:
            min_ = float(params.get('min'))
        except (ValueError, TypeError):
            min_ = None

        data = {
            "query": dict(bool={}),
            "size": limit,
            "from": offset,
            "post_filter": dict(bool={}),
        }

        should, must, post_filter = [], [], []
        query_list = keyword and keyword.replace('-', '_').split(',')
        search_fields = ["name^10.0", "keywords^8.0", "description^2.0"]

        if query_list:
            query = list(filter(None, query_list))
            should.extend([dict(multi_match={
                "query": ' '.join(query),
                "type": "phrase",
                "fields": search_fields,
                "boost": "10"
            }), dict(query_string={
                "query": ' '.join(map(lambda k: k + '*', query)),
                "fields": search_fields,
                "boost": "5"
            }), dict(multi_match={
                "query": ' '.join(query),
                "type": "most_fields",
                "fields": search_fields,
                "fuzziness": "AUTO"
            })])
        if brandId:
            must.append(dict(term={
                "brand.id": {
                    'value': brandId
                }
            }))
        if brandName:
            must.append(dict(match={
                "brand.name": brandName
            }))
        if max_ or min_:
            post_filter.append(dict(range={
                "calculated_price": {
                    "gte": min_,
                    "lte": max_,
                }
            }))
        post_filter.append(dict(term={
            "is_visible": "true"
        }))

        if should:
            data["query"]["bool"].update(dict(should=should))
        if must:
            data["query"]["bool"].update(dict(must=must))
        if post_filter:
            data["post_filter"]["bool"].update(dict(must=post_filter))
        if sort:
            data.update({"sort": get_sort_keys(sort, direction)})

        res = request.env['es.search'].query(index=product_index.name, body=data)
        hits_res = list(map(lambda r: r['_source'], res['hits']['hits']))
        total_hits = res['hits']['total']['value']

        meta = dict(pagination=dict(
            count=len(hits_res),
            total=total_hits,
            current_page=page,
            per_page=limit,
            total_pages=ceil(total_hits / int(limit))
        ))
        return json.dumps(dict(data=hits_res, meta=meta))

    @route('/api/product/live-search', type='http', methods=['GET'], auth='none', csrf=False)
    def product_live_search(self, keyword=None):
        product_index = request.env['es.index'].sudo().search(
            [('name', '=', 'product-template-live-search'), ('index_exists', '=', True)], limit=1)
        result = dict(data=[])
        if not product_index:
            result['error'] = "Missing ES index named 'product-template-live-search'! Please create this index in Odoo."

        query_list = keyword and keyword.replace('-', '_').split(',')

        if query_list and product_index:
            data = {
                "query": dict(bool={}),
                "size": 10,
                "post_filter": {
                    'bool': {
                        'must': [{'term': {
                            'is_visible': "true"
                        }
                        }, ]
                    }
                },
            }
            should = []
            search_fields = ['name']
            query = list(filter(None, query_list))
            should.extend([dict(multi_match={
                "query": ' '.join(query),
                "type": "phrase",
                "fields": search_fields,
                "boost": "10"
            }), dict(query_string={
                "query": ' '.join(map(lambda k: k + '*', query)),
                "fields": search_fields,
                "boost": "5"
            }), dict(multi_match={
                "query": ' '.join(query),
                "type": "most_fields",
                "fields": search_fields,
                "fuzziness": "AUTO"
            })])

            if should:
                data["query"]["bool"].update(dict(should=should))

            res = request.env['es.search'].query(index=product_index.name, body=data)
            result['data'] = list(map(lambda r: r['_source'], res['hits']['hits']))

        return json.dumps(result)
