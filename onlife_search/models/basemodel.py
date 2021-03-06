from odoo import api, models

PRODUCT_FIELD_MAPPING = dict([('sinc_id', 'id'),
                              ('id', 'product_id'),
                              ('default_price', 'price'),
                              ('list_price', 'calculated_price'),
                              ('public_categ_ids', 'categories'),
                              ('sale_ok', 'is_visible'),
                              ('marca_id', 'brand')])


def update_data_keys(dict_):
    new_dict, images = {}, []
    for k, v in dict_.items():
        new_k = PRODUCT_FIELD_MAPPING.get(k)
        if new_k:
            new_dict[new_k] = dict_[k]
        elif k.startswith('image'):
            images.append({'product_id': dict_['id'],
                           'url_standard': dict_[k]})
        else:
            new_dict[k] = v
    if images:
        new_dict['images'] = images
    return new_dict


class BaseModelExtend(models.AbstractModel):
    _name = 'basemodel.extend'
    _description = 'Basemodel Extension'

    def _register_hook(self):
        origin_search_read_json = models.AbstractModel.search_read_json

        @api.model
        def search_read_json(self, domain=None, fields=None, offset=0, limit=None, order=None):
            product_model = self._name == 'product.template'
            if product_model:
                fields += ['name', 'sinc_id', 'sale_ok']
            # By default, Odoo performs search_read as is, so use context to define the language
            res = origin_search_read_json(
                self=self.with_context(lang='es_GT') if product_model else self,
                domain=domain,
                fields=fields,
                offset=offset,
                limit=limit,
                order=order)
            return [update_data_keys(vals) for vals in res] if product_model else res

        models.AbstractModel.search_read_json = search_read_json
        return super(BaseModelExtend, self)._register_hook()
