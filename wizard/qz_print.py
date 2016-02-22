# -*- coding: utf-8 -*-
from osv import fields, osv
from zebra import zebra
import re


class QzPrint(osv.osv):
    _name = 'qz.print'
    _description = 'Qz Print Labels'

    _columns = {
        'copies': fields.integer('Num of Copy:', required=True),
    }

    _defaults = {

        'copies': 1,
    }

    # Get default queue name
    def get_queue(self, cr, uid, field_names=None, arg=None, context=None):
        result = {}
        pool_obj = self.pool.get('qz.config')
        pool_ids = pool_obj.search(cr, uid, [('qz_default', '=', 1)])
        if pool_ids:
            for i in pool_obj.browse(cr, uid, pool_ids, context=context):
                result = i.qz_printer.system_name
            return result

    # Prepare EPL data (escaped)

    def prepare_epl_data(self, cr, uid, field_names=None, arg=None, context=None):
        result = {}
        pool_obj = self.pool.get('qz.config')
        pool_ids = pool_obj.search(cr, uid, [('qz_default', '=', 1)])
        if pool_ids:
            for i in pool_obj.browse(cr, uid, pool_ids, context=context):
                for fields in i.qz_field_ids:

                    # Format: Bp1,p2,p3,p4,p5,p6,p7,p8,"DATA"\n

                    if fields.qz_field_type == 'barcode':
                        data = []
                        data += ('B' + str(fields.h_start_p1) + ',' +
                                 str(fields.v_start_p2) + ',' +
                                 str(fields.rotation_p3) + ',' +
                                 str(fields.bar_sel_p4) + ',' +
                                 str(fields.n_bar_w_p5) + ',' +
                                 str(fields.w_bar_w_p6) + ',' +
                                 str(fields.bar_height_p7) + ',' +
                                 str(fields.human_read_p8))
                                 #str(fields.qz_field_id.id.internal_reference) + '"' + '\n')

                    # text field Format: Ap1,p2,p3,p4,p5,p6,p7,"DATA"\n
                    else:
                        data2 = []
                        data2 += ('A' + str(fields.h_start_p1) + ',' +
                                  str(fields.v_start_p2) + ',' +
                                  str(fields.rotation_p3) + ',' +
                                  str(fields.font_p4) + ',' +
                                  str(fields.h_multiplier_p5) + ',' +
                                  str(fields.v_multiplier_p6) + ',' +
                                  str(fields.n_r_p7) + ',' + '"' )
                                  #str(fields.qz_field_id.internal_reference) + '"' + '\n')

                """
                    Example of ELP commands to send

                    N
                    A40,80,0,4,1,1,N,"Tangerine Duck 4.4%"
                    A40,198,0,3,1,1,N,"Duty paid on 39.9l"
                    A40,240,0,3,1,1,N,"Gyle: 127     Best Before: 16/09/2011"
                    A40,320,0,4,1,1,N,"Pump & Truncheon"
                    P1

                 """

                result = 'N\n' +  str(data) + '\n' + str(data2) + '\n' + 'P1\n'
                print result
                return result

    # Print EPL data
    def send_epl_data(self, cr, uid, ids, copies, context=None):

        z = zebra()
        queue = self.get_queue(cr, uid, context=context)
        z.setqueue(queue)
        conf_obj = self.pool.get('qz.config')
        conf_id = conf_obj.search(cr, uid, [('qz_default', '=', 1)])
        if conf_id:
            for x in conf_obj.browse(cr, uid, conf_id):
                thermal = x.qz_direct_thermal
                h = x.qz_label_height
                gap = x.qz_label_gap
                height = [h, gap]
                width = x.qz_label_width
        z.setup(direct_thermal=thermal, label_height=height, label_width=width)
        commands = self.prepare_epl_data(cr, uid, context=context)
        z.output(commands)


QzPrint()
