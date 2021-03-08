import json
from math import ceil

from odoo.http import Controller, route, request

SORT_KEY_MAP = dict([('name', 'name.keyword'),
                     ('price', 'calculated_price')])
SORTING_DIRECTION = ('asc', 'desc')


def get_sort_keys(s, d):
    sort_keys = []
    sort_dir = d and d.lower()
    for s_key in s.split(','):
        s_key = SORT_KEY_MAP.get(s_key, s_key)
        sort_keys.append({s_key: sort_dir} if sort_dir in SORTING_DIRECTION else s_key)
    return sort_keys


class OnlifeSearchAPI(Controller):

    @route('/api/product/search', type='http', methods=['GET'], auth='user', csrf=False)
    def product_fuzzy_search(self, keyword=None, brandId=None, brandName=None,
                             limit=20, page=0, sort=None, direction=None):
        product_index = request.env['es.index'].sudo().search([('model_id.model', '=', 'product.template')], limit=1)

        # Prevent from overriding the global functions max and min
        params = request.params
        max_, min_ = params.get('max', 0), params.get('min', 0)

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
        if keyword:
            must.append(dict(multi_match={
                "query": ' '.join(keyword.split(',')),
                "fields": ["name^6.0", "description^2.0"],
                "fuzziness": "AUTO"
            }))
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

        if max_ or min_:
            data.update(dict(post_filter={
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

        hits = res['hits']['hits']
        hits_res = map(lambda r: r['_source'], hits)
        total_hits = res['hits']['total']['value']

        meta = dict(meta=dict(pagination=dict(count=len(hits), total=total_hits, current_page=page, per_page=limit,
                                              total_pages=ceil(total_hits / int(limit)))))

        return json.dumps(dict(data=list(hits_res), meta=meta))
