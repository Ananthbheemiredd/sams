def calculate_salary(data):
    """
    Calculates salary from SalaryComponent payload
    """

    basic = data.basic_salary or 0
    hra = data.hra or 0
    food = data.food_allowance or 0
    special = data.special_allowance or 0
    other = data.other_allowance or 0

    gross_salary = basic + hra + food + special + other

    pf_employee = data.pf_employee or 0
    pf_employer = data.pf_employer or 0
    professional_tax = data.professional_tax or 0
    lop_amount = data.lop_amount or 0

    net_salary = gross_salary - (pf_employee + professional_tax + lop_amount)

    return {
        "total_ctc": gross_salary * 12,
        "net_salary": net_salary,
        "pf_employee": pf_employee,
        "pf_employer": pf_employer,
        "professional_tax": professional_tax
    }








