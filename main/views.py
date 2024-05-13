from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
import decimal, ast
import simplejson as json
from .db_models import room, analysis_data
from . import encryption as enc
from . import create_plot as plot

sessions = room.objects.all()
preset_data = analysis_data.objects.all()

def start_page(request):
    request.session.flush()
    request.session['is_logged_into_session'] = 0
    return render(request, 'main/start_page.html')

def session_login(request):
    return render(request, 'main/session_login.html')

def redirect_view(request):
    response = redirect('/start_page')
    return response

def sw_impact(request):
    extraFactors = 0
    max_factors = 100
    s_names = [f"S_{i}" for i in range(1, max_factors + 1)]
    w_names = [f"W_{i}" for i in range(1, max_factors + 1)]
    o_names = [f"O_{i}" for i in range(1, max_factors + 1)]
    t_names = [f"T_{i}" for i in range(1, max_factors + 1)]

    request.session['p1_factors'] = []
    request.session['p1_weights'] = []
    request.session['p1_extra_factors'] = []

    s, rs = get_main_data(request, s_names)
    w, rw = get_main_data(request, w_names)
    o, ro = get_main_data(request, o_names)
    t, rt = get_main_data(request, t_names)

    request.session['p1_factors'] = s, w, o, t
    request.session['p1_weights'] = rs, rw, ro, rt
    request.session['p1_extra_factors'] = extraFactors

    preset_2p_values = {}
    x = len(max(s,w,o,t, key=len))
    if    (((int(x)-4))>0): 
            extraFactors = (int(x)-4)
            request.session['p1_extra_factors'] = extraFactors
    if request.session.get('is_logged_into_session') == 1:
        preset_2p_values = {
            'Svals': ast.literal_eval(request.session.get('p2_inputs'))[0],
            'Wvals': ast.literal_eval(request.session.get('p2_inputs'))[1]
        }
    else:
        preset_2p_values = {}
    s_len = len(s)
    w_len = len(w)

    context = {
        's_weights': s,
        'w_weights': w,
        's_weights_len': s_len,
        'w_weights_len': w_len,
        'sw_weights_len': s_len+w_len,
        'preset_2p_values_json': json.dumps(preset_2p_values),
        'extraFactors': extraFactors
    }
    return render(request, 'main/sw_impact.html', context)

def sw_impact_out(request):
    s, s_len = ( request.session.get('p1_factors')[0], len((request.session.get('p1_factors')[0])) )
    w, w_len = ( request.session.get('p1_factors')[1], len((request.session.get('p1_factors')[1])) )

    weights = []
    weights.extend(s)
    weights.extend(w)

    rs, rs_len = ( request.session.get('p1_weights')[0], len((request.session.get('p1_weights')[0])) )
    rw, rw_len = ( request.session.get('p1_weights')[1], len((request.session.get('p1_weights')[1])) )
    rsw,r_w,r_s = [],[],[]

    s_values, s_factor_names = get_factor_values(request, 'Svals', s_len)
    w_values, w_factor_names = get_factor_values(request, 'Wvals', w_len)

    values = []
    values.extend(s_values)
    values.extend(w_values)
    rsw.extend(rs)
    rsw.extend(rw)
    request.session['sum_sw'] = []
    request.session['eval_sw'] = []
    for k in range(len(values)):
        values[k] = list(map(lambda value: '0' if value == '' else value, values[k]))
    for k in range(len(values)):
        s = 0
        for v in values[k]:
            s += float(v)
        request.session['sum_sw'].append(s)
    for i in range(len(request.session.get('sum_sw'))):
        request.session['eval_sw'].append(int(decimal.Decimal(request.session['sum_sw'][i])+decimal.Decimal(rsw[i])))
    for i in range(len(values)):
        values[i].insert(i, None)

    r_s.extend(rs)
    values_s = []
    values_s.extend(s_values)
    request.session['sum_s'] = []
    request.session['eval_s'] = []
    request.session['p2_inputs'] = []
    for k in range(len(values_s)):
        values_s[k] = list(map(lambda value: '0' if value == '' else value, values_s[k]))
    request.session['p2_inputs'].append([item for sublist in values_s for item in sublist])
    for k in range(len(values_s)):
        s = 0
        for v in values_s[k]:
            s += float(v)
        request.session['sum_s'].append(s)
    for i in range(len(values_s)):
        request.session['eval_s'].append(int(decimal.Decimal(request.session['sum_s'][i])+decimal.Decimal(rsw[i])))

    r_w.extend(rw)
    values_w = []
    values_w.extend(w_values)
    request.session['sum_w'] = []
    request.session['eval_w'] = []
    for k in range(len(values_w)):
        values_w[k] = list(map(lambda value: '0' if value == '' else value, values_w[k]))
    request.session['p2_inputs'].append([item for sublist in values_w for item in sublist])
    for k in range(len(values_w)):
        s = 0
        for v in values_w[k]:
            s += float(v)
        request.session['sum_w'].append(s)
    for i in range(len(values_w)):
        request.session['eval_w'].append(int(decimal.Decimal(request.session['sum_w'][i])+decimal.Decimal(r_w[i])))

    context = {
        'weights': weights,
        's_weights_len': s_len,
        'w_weights_len': w_len,
        'sw_weights_len': s_len + w_len,
        'values': values,
        'sums': request.session.get('sum_sw'),
    }
    return render(request, 'main/sw_impact_out.html', context)


def ot_impact(request):
    o, o_len = ( request.session.get('p1_factors')[2], len((request.session.get('p1_factors')[2])) )
    t, t_len = ( request.session.get('p1_factors')[3], len((request.session.get('p1_factors')[3])) )

    if request.session.get('is_logged_into_session') == 1:
            preset_3p_values = {
            'Ovals': ast.literal_eval(request.session.get('p3_inputs'))[0],
            'Tvals': ast.literal_eval(request.session.get('p3_inputs'))[1]
        }
    else:
        preset_3p_values = {}
    o_len = len(o)
    t_len = len(t)

    context = {
        'o_weights': o,
        't_weights': t,
        'o_weights_len': o_len,
        't_weights_len': t_len,
        'ot_weights_len': o_len + t_len,
        'preset_3p_values_json': json.dumps(preset_3p_values)
    }
    return render(request, 'main/ot_impact.html', context)

def ot_impact_out(request):
    o, o_len = ( request.session.get('p1_factors')[2], len((request.session.get('p1_factors')[2])) )
    t, t_len = ( request.session.get('p1_factors')[3], len((request.session.get('p1_factors')[3])) )
    weights = []
    weights.extend(o)
    weights.extend(t)

    request.session['p3_inputs']=[]

    o_values, o_factor_names = get_factor_values(request, 'Ovals', o_len)
    for k in range(len(o_values)):
        o_values[k] = list(map(lambda value: '0' if value == '' else value, o_values[k]))
    request.session['p3_inputs'].append([item for sublist in o_values for item in sublist])

    t_values, t_factor_names = get_factor_values(request, 'Tvals', t_len)
    for k in range(len(t_values)):
        t_values[k] = list(map(lambda value: '0' if value == '' else value, t_values[k]))
    request.session['p3_inputs'].append([item for sublist in t_values for item in sublist])

    values = []
    values.extend(o_values)
    values.extend(t_values)
    request.session['sum_ot'] = []
    for k in range(len(values)):
        s = 0
        for v in values[k]:
            s += float(v)
        request.session['sum_ot'].append(s)
    for i in range(len(values)):
        values[i].insert(i, None)
    context = {
        'weights': weights,
        'o_weights_len': o_len,
        't_weights_len': t_len,
        'ot_weights_len': o_len + t_len,
        'values': values,
        'sums': request.session.get('sum_ot'),
    }
    return render(request, 'main/ot_impact_out.html', context)


def possibilities(request):
    preset_4p_values = {}
    if request.session.get('is_logged_into_session') == 1:
            preset_4p_values = {
            'preset_4p_values': ast.literal_eval(request.session.get('p4_inputs'))
        }
            print(ast.literal_eval(request.session.get('p4_inputs')))
    else:
        preset_4p_values = {}
    o, o_len = ( request.session.get('p1_factors')[2], len((request.session.get('p1_factors')[2])) )
    t, t_len = ( request.session.get('p1_factors')[3], len((request.session.get('p1_factors')[3])) )
    ro, ro_len = ( request.session.get('p1_weights')[2], len((request.session.get('p1_weights')[2])) )
    rt, rt_len = ( request.session.get('p1_weights')[3], len((request.session.get('p1_weights')[3])) )
    ot_sum = request.session.get('sum_ot')
    eval = []
    rot = []
    rot.extend(ro)
    rot.extend(rt)
    for i in range(len(ot_sum)):
        eval.append(decimal.Decimal(ot_sum[i])+decimal.Decimal(rot[i]))
    weights = []
    weights.extend(o)
    weights.extend(t)
    context = {
        'weights': weights,
        'sums': eval,
        'preset_4p_values_json': preset_4p_values
        }
    request.session['sums_pos_eval'] = [int(x) for x in eval]
    return render(request, 'main/possibilities.html', context)


def result(request):
    preset_5p_values = {}
    if request.session.get('is_logged_into_session') == 1:
        preset_5p_values = {
            'Oinf': ast.literal_eval(request.session.get('p5_inputs'))[0], 
            'Tinf': ast.literal_eval(request.session.get('p5_inputs'))[1]
        }
    else:
        preset_5p_values = {}
    s, s_len = ( request.session.get('p1_factors')[0], len((request.session.get('p1_factors')[0])) )
    w, w_len = ( request.session.get('p1_factors')[1], len((request.session.get('p1_factors')[1])) )
    o, o_len = ( request.session.get('p1_factors')[2], len((request.session.get('p1_factors')[2])) )
    t, t_len = ( request.session.get('p1_factors')[3], len((request.session.get('p1_factors')[3])) )
    possibilities = request.POST.getlist("pos")
    request.session['p4_inputs'] = possibilities
    print(possibilities)
    for k in range(len(possibilities)):
        if possibilities[k] == '':
            possibilities[k] = '1'
    request.session['pos_eval'] = possibilities
    pos_eval = request.session['pos_eval']
    
    context = {
        's_weights': s,
        'w_weights': w,
        's_weights_len': s_len,
        'w_weights_len': w_len,
        'sw_weights_len': s_len + w_len,
        'o_weights': o,
        't_weights': t,
        'o_weights_len': o_len,
        't_weights_len': t_len,
        '2x_o_weights_len': o_len*2,
        '2x_t_weights_len': t_len*2,
        'ot_weights_len': o_len + t_len,
        's_eval': request.session.get('eval_s'),
        'w_eval': request.session.get('eval_w'),
        'pos_eval': pos_eval,
        'preset_5p_values_json': json.dumps(preset_5p_values)
    }
    return render(request, 'main/result.html', context)

def result_out(request):
    s, s_len = ( request.session.get('p1_factors')[0], len((request.session.get('p1_factors')[0])) )
    w, w_len = ( request.session.get('p1_factors')[1], len((request.session.get('p1_factors')[1])) )
    o, o_len = ( request.session.get('p1_factors')[2], len((request.session.get('p1_factors')[2])) )
    t, t_len = ( request.session.get('p1_factors')[3], len((request.session.get('p1_factors')[3])) )
    oinf_values, o_factor_names = get_factor_values(request, 'Oinf', o_len)
    tinf_values, t_factor_names = get_factor_values(request, 'Tinf', t_len)

    for k in range(len(oinf_values)):
        oinf_values[k] = list(map(lambda x: '0' if x == '' else x, oinf_values[k]))

    for k in range(len(tinf_values)):
        tinf_values[k] = list(map(lambda x: '0' if x == '' else x, tinf_values[k]))
        
    inf = []
    inf.extend(oinf_values)
    inf.extend(tinf_values)

    for k in range(len(inf)):
        inf[k] = list(map(lambda x: '0' if x == '' else x, inf[k]))

    request.session['p5_inputs'] = [[item for sublist in oinf_values for item in sublist], [item for sublist in tinf_values for item in sublist]]

    weights = []
    weights.extend(s)
    weights.extend(w)
    sums_inf = []
    sw_sums = request.session.get('eval_sw')
    pos_eval = request.session.get('pos_eval')

    final_eval = []

    for i in range(len(oinf_values)+len(tinf_values)):
        mid_sums = []
        s = 0

        for k in range(len(sw_sums)):
            mid_sum = decimal.Decimal(inf[i][k])
            s += mid_sum
            mid_sums.append(mid_sum)
        sums_inf.append(mid_sums)
        final_eval.append(round(s,2))

    ot_addition_to_weigths = [[decimal.Decimal(x) for x in (final_eval[0:len(oinf_values)])],[decimal.Decimal(x) for x in (final_eval[len(oinf_values):])]]
    inputted_ot_weights = [[decimal.Decimal(item) for item in sublist] for sublist in [request.session.get('p1_weights')[2],request.session.get('p1_weights')[3]]]

    ot_weights = []
    for sublist1, sublist2 in zip(ot_addition_to_weigths, inputted_ot_weights):
        sum_sublist = [round((a + b),2) for a, b in zip(sublist1, sublist2)]
        ot_weights.append(sum_sublist)

    ot_weights_flattenned = [str(item) for sublist in ot_weights for item in sublist]

    pos_eval_decimals = [decimal.Decimal(item) for item in pos_eval]
    pos_eval_decimals_lists = [pos_eval_decimals[0:len(oinf_values)],pos_eval_decimals[len(oinf_values):]]

    total_ot_weights = []
    for sublist1, sublist2 in zip(ot_weights, pos_eval_decimals_lists):
        sum_sublist = [round(a * b,2) for a, b in zip(sublist1, sublist2)]
        total_ot_weights.append(sum_sublist)

    total_ot_weights_flattenned = [item for sublist in total_ot_weights for item in sublist]

    sw_plot, sw_legend = plot.create_plot([request.session.get('p1_factors')[0],request.session.get('p1_factors')[1]],
                [[decimal.Decimal(y) for y in (sw_sums[0:s_len])],[decimal.Decimal(y) for y in (sw_sums[s_len:])]], "sw")
    ot_plot, ot_legend = plot.create_plot([request.session.get('p1_factors')[2],request.session.get('p1_factors')[3]],
                total_ot_weights,"ot")

    import uuid
    room_uuid = str(uuid.uuid4())

    context = {
        's_weights': s,
        'w_weights': w,
        'weights': weights,
        's_weights_len': s_len,
        'w_weights_len': w_len,
        'sw_weights_len': s_len + w_len,
        'sw_weights_len_range': range(s_len + w_len),
        'o_weights': o,
        't_weights': t,
        'o_weights_len': o_len,
        't_weights_len': t_len,
        'ot_weights_len': o_len + t_len,
        'sw_sums': sw_sums,
        'inf': inf,
        'sums_inf': sums_inf,
        'final_eval': total_ot_weights_flattenned,
        'ot_weights_flattenned': ot_weights_flattenned,
        'pos_eval': pos_eval,
        'uuid': room_uuid,
        'isLoggedIn': request.session.get('is_logged_into_session'),
        'oinf_values': oinf_values,
        'tinf_values': tinf_values,
        'sw_plot': sw_plot,
        'ot_plot': ot_plot,
        'sw_legend': sw_legend,
        'ot_legend': ot_legend
    }
    return render(request, 'main/result_out.html', context)

def room_handler(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        keyword = data.get('userInput', '')
        print("keyword is: ",keyword)
        room_uuid = data.get('roomUuid', '') 
        if (room_uuid == ""):
            print("room_uuid is empty")
            keyword = request.session['keyword']
            room_uuid = request.session['room_uuid']
            existing_session = analysis_data.objects.get(uuid=room_uuid)

            existing_session.p1_factors = enc.encode_token(str(request.session.get('p1_factors')), keyword)
            existing_session.p1_weights = enc.encode_token(str(request.session.get('p1_weights')), keyword)
            existing_session.p1_extra_factors = enc.encode_token(str(request.session.get('p1_extra_factors')), keyword)
            existing_session.p2_inputs = enc.encode_token(str(request.session.get('p2_inputs')), keyword)
            existing_session.p3_inputs = enc.encode_token(str(request.session.get('p3_inputs')), keyword)
            existing_session.p4_inputs = enc.encode_token(str(request.session.get('p4_inputs')), keyword)
            print(existing_session.p4_inputs)
            existing_session.p5_inputs = enc.encode_token(str(request.session.get('p5_inputs')), keyword)
            
            existing_session.save()
        else:
            new_session = room(uuid=room_uuid, hash=enc.encode_token(room_uuid,keyword))
            new_session.save()
            new_session = analysis_data(uuid=room_uuid, 
                                        p1_factors=enc.encode_token(str(request.session.get('p1_factors')), keyword), 
                                        p1_weights=enc.encode_token(str(request.session.get('p1_weights')), keyword),
                                        p1_extra_factors=enc.encode_token(str(request.session.get('p1_extra_factors')), keyword),
                                        p2_inputs=enc.encode_token(str(request.session.get('p2_inputs')), keyword),
                                        p3_inputs=enc.encode_token(str(request.session.get('p3_inputs')), keyword),
                                        p4_inputs=enc.encode_token(str(request.session.get('p4_inputs')), keyword),
                                        p5_inputs=enc.encode_token(str(request.session.get('p5_inputs')), keyword))
            new_session.save()
        
        return JsonResponse({"message": "Received: 200"})
    return JsonResponse({"error": "Invalid request"}, status=400)

def get_main_data(request, names):
    values = []
    r_values = []
    for name in names:
        value = request.POST.get(name)
        if value is not None and value != '':
            values.append(value)
            r_values.append(request.POST.get('R'+name))
    return values, r_values

def get_factor_values(request, factor_name, factor_len):
    factor_values = []
    factor_names = []
    for i in range(factor_len):
        unique_factor_name = factor_name+str(i+1)
        factor_values.append(request.POST.getlist(unique_factor_name))
        factor_names.append(unique_factor_name)
    return factor_values, factor_names

def validate_session(request):
    if request.method == 'POST':
        session_uuid = request.POST.get('session_uuid')
        session_keyword = request.POST.get('session_keyword')
        try: 
            decoded_hash = enc.decode_token((room.objects.get(uuid=session_uuid).hash), session_keyword)
        except room.DoesNotExist:
            messages.error(request, 'Комбинация UUID сессии и ключевого слова неверная. Попробуйте снова.')
            return redirect('session_login')
        if (room.objects.filter(uuid=session_uuid).count() != 0) and (session_uuid == decoded_hash):
            request.session['room_uuid'] = session_uuid
            request.session['is_logged_into_session'] = 1
            request.session['keyword'] = session_keyword
            request.session['p1_factors'] = enc.decode_token((analysis_data.objects.get(uuid=session_uuid).p1_factors),session_keyword)
            request.session['p1_weights'] = enc.decode_token((analysis_data.objects.get(uuid=session_uuid).p1_weights),session_keyword)
            request.session['p1_extra_factors'] = enc.decode_token((analysis_data.objects.get(uuid=session_uuid).p1_extra_factors),session_keyword)
            request.session['p2_inputs'] = enc.decode_token((analysis_data.objects.get(uuid=session_uuid).p2_inputs),session_keyword)
            request.session['p3_inputs'] = enc.decode_token((analysis_data.objects.get(uuid=session_uuid).p3_inputs),session_keyword)
            request.session['p4_inputs'] = enc.decode_token((analysis_data.objects.get(uuid=session_uuid).p4_inputs),session_keyword)
            request.session['p5_inputs'] = enc.decode_token((analysis_data.objects.get(uuid=session_uuid).p5_inputs),session_keyword)
            return redirect('/factor_matrix/')
        else:
            messages.error(request, 'Комбинация UUID сессии и ключевого слова неверная. Попробуйте снова.')
            return redirect('session_login')
    return render(request, 'your_form_template_name.html')

def factor_matrix(request):
    if request.session.get('is_logged_into_session') == 1:
        extra_factors = int(request.session.get('p1_extra_factors'))
        preset_factors = {
            'input_s': ast.literal_eval(request.session.get('p1_factors'))[0],
            'input_w': ast.literal_eval(request.session.get('p1_factors'))[1],
            'input_o': ast.literal_eval(request.session.get('p1_factors'))[2],
            'input_t': ast.literal_eval(request.session.get('p1_factors'))[3]
        }
        preset_weights = {
            'input_s_r': ast.literal_eval(request.session.get('p1_weights'))[0],
            'input_w_r': ast.literal_eval(request.session.get('p1_weights'))[1],
            'input_o_r': ast.literal_eval(request.session.get('p1_weights'))[2],
            'input_t_r': ast.literal_eval(request.session.get('p1_weights'))[3]
        }
    else:
        extra_factors = 0
        preset_factors = {}
        preset_weights = {}
    return render(request, 'main/factor_matrix.html', {'preset_factors': preset_factors, 'extra_factors': extra_factors, 'preset_weights': preset_weights})