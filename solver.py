import pulp
from schemas import OptimizeRequest, DirectiveInterpretation, HourlyPlan

def solve_gridwise(request: OptimizeRequest, directives: list[DirectiveInterpretation]):
    # প্রবলেম সেটআপ: লক্ষ্য হলো কস্ট মিনিমাইজ (কমানো)
    prob = pulp.LpProblem("GridWise_Optimization", pulp.LpMinimize)
    
    # ডেটা পার্সিং
    hours_data = {h.hour: h for h in request.hours}
    bat = request.battery
    
    # ডিফল্ট প্যারামিটার সেট করা (যা LLM-এর ডিরেক্টিভ অনুযায়ী পরে চেঞ্জ হবে)
    effective_solar = {h: hours_data[h].solar_kwh for h in range(24)}
    min_reserve = {h: bat.minimum_energy_kwh for h in range(24)}
    max_charge = {h: bat.max_charge_kwh_per_hour for h in range(24)}
    max_discharge = {h: bat.max_discharge_kwh_per_hour for h in range(24)}
    max_grid = {h: None for h in range(24)}
    
    # LLM থেকে পাওয়া ডিরেক্টিভগুলো অপ্টিমাইজারে অ্যাপ্লাই করা
    for d in directives:
        if not d.applies or not d.structured_adjustment:
            continue
        adj = d.structured_adjustment
        hours = adj.hours or []
        dtype = d.directive_type
        
        for h in hours:
            if h < 0 or h > 23: continue
            
            if dtype == "solar_reduction" and adj.factor is not None:
                effective_solar[h] = hours_data[h].solar_kwh * adj.factor
            elif dtype == "minimum_battery_reserve" and adj.minimum_energy_kwh is not None:
                min_reserve[h] = max(min_reserve[h], adj.minimum_energy_kwh)
            elif dtype == "no_charge_window":
                max_charge[h] = 0
            elif dtype == "no_discharge_window":
                max_discharge[h] = 0
            elif dtype == "max_grid_window" and adj.max_grid_kwh is not None:
                if max_grid[h] is None:
                    max_grid[h] = adj.max_grid_kwh
                else:
                    max_grid[h] = min(max_grid[h], adj.max_grid_kwh)
                    
    # ভ্যারিয়েবল ডিক্লেয়ার করা
    grid_kwh = pulp.LpVariable.dicts("grid", range(24), lowBound=0)
    solar_used = pulp.LpVariable.dicts("solar_used", range(24), lowBound=0)
    charge = pulp.LpVariable.dicts("charge", range(24), lowBound=0)
    discharge = pulp.LpVariable.dicts("discharge", range(24), lowBound=0)
    energy_after = pulp.LpVariable.dicts("energy_after", range(24), lowBound=0)
    
    # অবজেক্টিভ: টোটাল কস্ট কমানো
    prob += pulp.lpSum([grid_kwh[h] * hours_data[h].tariff_bdt_per_kwh for h in range(24)])
    
    # কনস্ট্রেইন্ট (রুলস)
    for h in range(24):
        # এনার্জি ব্যালেন্স ইকুয়েশন
        prob += grid_kwh[h] + solar_used[h] + discharge[h] == hours_data[h].demand_kwh + charge[h]
        
        # সোলার এবং ব্যাটারি লিমিটেশন
        prob += solar_used[h] <= effective_solar[h]
        prob += charge[h] <= max_charge[h]
        prob += discharge[h] <= max_discharge[h]
        
        if max_grid[h] is not None:
            prob += grid_kwh[h] <= max_grid[h]
            
        # ব্যাটারি স্টেট এবং ক্যাপাসিটি
        prev_e = energy_after[h-1] if h > 0 else bat.initial_energy_kwh
        prob += energy_after[h] == prev_e + charge[h] - discharge[h]
        prob += energy_after[h] >= min_reserve[h]
        prob += energy_after[h] <= bat.capacity_kwh
        
    # রুল: দিন শেষে ব্যাটারির চার্জ শুরুর চার্জের সমান হতে হবে
    prob += energy_after[23] == bat.initial_energy_kwh
    
    # সলভার রান করা
    prob.solve(pulp.PULP_CBC_CMD(msg=False))
    
    # রেজাল্টগুলো JSON-এর জন্য সাজানো
    hourly_plan = []
    tot_grid = 0.0
    tot_cost = 0.0
    peak_grid = 0.0
    
    for h in range(24):
        g_val = round(grid_kwh[h].varValue or 0.0, 3)
        s_val = round(solar_used[h].varValue or 0.0, 3)
        c_val = round(charge[h].varValue or 0.0, 3)
        d_val = round(discharge[h].varValue or 0.0, 3)
        e_val = round(energy_after[h].varValue or 0.0, 3)
        
        # ব্যাটারি অ্যাকশন (Charge/Discharge/Idle) বের করা
        net = c_val - d_val
        if net > 0.001:
            action = "charge"
            bat_val = net
        elif net < -0.001:
            action = "discharge"
            bat_val = abs(net)
        else:
            action = "idle"
            bat_val = 0.0
            
        tot_grid += g_val
        tot_cost += g_val * hours_data[h].tariff_bdt_per_kwh
        if g_val > peak_grid:
            peak_grid = g_val
            
        plan_entry = HourlyPlan(
            hour=h,
            grid_kwh=g_val,
            solar_used_kwh=s_val,
            battery_action=action,
            battery_kwh=round(bat_val, 3),
            battery_energy_after_kwh=e_val
        )
        hourly_plan.append(plan_entry)
        
    return {
        "hourly_plan": hourly_plan,
        "total_grid_kwh": round(tot_grid, 3),
        "total_cost_bdt": round(tot_cost, 3),
        "peak_grid_kwh": round(peak_grid, 3)
    }