from odoo import api, models

PRODUCT_FIELD_MAPPING = {'list_price': 'calculated_price',
                         'public_categ_ids': 'categories',
                         'sale_ok': 'is_visible',
                         'marca_id': 'brand'}


def update_data_keys(dict_):
    new_dict = {}
    images = []
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
        origin_read_json = models.AbstractModel.read_json

        @api.model
        def read_json(self, fields=None, load='_classic_read'):
            res = origin_read_json(self=self, fields=fields, load=load)
            return [update_data_keys(vals) for vals in res]

        models.AbstractModel.read_json = read_json
        return super(BaseModelExtend, self)._register_hook()
