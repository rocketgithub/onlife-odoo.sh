import json
import math

from odoo.http import Controller, route, request


def get_sort_keys(s, d):
    sort_keys = []
    for s_key in s.split(','):
        if s_key == 'name':
            s_key = 'name.keyword'
        if s_key == 'price':
            s_key = 'calculated_price'
        if d and d in ('asc', 'desc'):
            sort_keys.append({s_key: d})
        else:
            sort_keys.append(s_key)
    return sort_keys


class OnlifeSearchAPI(Controller):

    @route('/api/product/search', type='http', methods=['GET'], auth='none', csrf=False)
    def product_fuzzy_search(self, keyword=None, brandId=None, brandName=None,
                             limit=20, page=0, sort=None, direction=None):
        product_index = request.env['es.index'].sudo().search([('model_id.model', '=', 'product.template')], limit=1)

        # Prevent from overriding the global functions max and min
        params = request.params
        max_ = params.get('max', 0)
        min_ = params.get('min', 0)

        try:
            offset = int(page) * int(limit)
        except ValueError:
            offset = 0

        data = {
            "query": dict(bool={}),
            "size": limit,
            "from": offset,
        }

        must = []

        # TODO: Support multiple queries using another must key for comma-separated search queries
        if keyword:
            must.append(dict(fuzzy={
                "name": keyword
            }))

        # It is assumed that marca_id (the brand field) is indexed
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

        if must:
            data["query"]["bool"].update(dict(must=must))

        # It is assumed that list_price is indexed
        if max_ or min_:
            data["query"]["bool"].update(dict(filter={
                "range": {
                    'calculated_price': {
                        "gte": float(min_) or None,
                        "lte": float(max_) or None,
                    }
                }
            }))

        if sort:
            data.update({"sort": get_sort_keys(sort, direction)})

        res = request.env['es.search'].query(index=product_index.name, body=data)

        hits_res = map(lambda r: r['_source'], res['hits']['hits'])
        total_hits = res['hits']['total']['value']

        meta = {'meta': {
            "pagination": {
                "count": limit,
                "total": total_hits,
                "current_page": page,
                "per_page": limit,
                "total_pages": math.ceil(total_hits / int(limit))
            }
        }}

        return json.dumps(dict(data=list(hits_res), meta=meta))
