#include <Python.h>
#include <stdio.h>
#include <math.h>


// linear simple
static PyObject* calculations_new_price(PyObject *self, PyObject *args)
{
    int startmenge_gueter;
    float gp0;
    int aktuelle_menge_des_gutes;
    // gueter preis gp0 = sum(gm0..3) / gm0 

    if (!PyArg_ParseTuple(args, "ii", &startmenge_gueter, &aktuelle_menge_des_gutes))
        return NULL;

    gp0 = startmenge_gueter / aktuelle_menge_des_gutes;
    return Py_BuildValue("f", gp0);
}

// tests
static PyObject* calculations_new_price_test(PyObject *self, PyObject *args)
{
    double startmenge_eines_gutes;
    double gesamtmenge_aller_gueter;
    double gesamtmenge_geld;
    double aktuelle_menge_des_gutes;
    double gp0;

    if (!PyArg_ParseTuple(args, "dddd", &startmenge_eines_gutes, &gesamtmenge_aller_gueter, &gesamtmenge_geld, &aktuelle_menge_des_gutes))
        return NULL;

    gp0 = (( startmenge_eines_gutes / gesamtmenge_aller_gueter ) * gesamtmenge_geld ) / aktuelle_menge_des_gutes;
    return Py_BuildValue("d", gp0);
}

// tests
static PyObject* calculations_new_price_test1(PyObject *self, PyObject *args)
{
    double startmenge_eines_gutes;
    double aktuelle_menge_des_gutes;
    double ausgangspreis;
    double gp0;

    if (!PyArg_ParseTuple(args, "ddd", &startmenge_eines_gutes, &aktuelle_menge_des_gutes, &ausgangspreis))
        return NULL;

    
    gp0 = ausgangspreis * pow( startmenge_eines_gutes / aktuelle_menge_des_gutes, 2);
    return Py_BuildValue("d", gp0);
}

//Method definition object for this extension, these argumens mean:
//ml_name: The name of the method
//ml_meth: Function pointer to the method implementation
//ml_flags: Flags indicating special features of this method, such as
//          accepting arguments, accepting keyword arguments, being a
//          class method, or being a static method of a class.
//ml_doc:  Contents of this method's docstring
static PyMethodDef calculations_module_methods[] = { 
    {   
        "new_price",
        calculations_new_price,
        METH_VARARGS,
        "return the new price from a method defined in a C extension."
    },  
    {   
        "new_price_test",
        calculations_new_price_test,
        METH_VARARGS,
        "return the new price from a method defined in a C extension. different implementation"
    },  
    {   
        "new_price_test1",
        calculations_new_price_test1,
        METH_VARARGS,
        "return the new price from a method defined in a C extension. different implementation"
    },  
    {NULL, NULL, 0, NULL}
};

//Module definition
//The arguments of this structure tell Python what to call your extension,
//what it's methods are and where to look for it's method definitions
static struct PyModuleDef calculations_definition = { 
    PyModuleDef_HEAD_INIT,
    "calculations",
    "A Python module holds calculations methods written in C",
    -1, 
    calculations_module_methods
};

//Module initialization
//Python calls this function when importing your extension. It is important
//that this function is named PyInit_[[your_module_name]] exactly, and matches
//the name keyword argument in setup.py's setup() call.
PyMODINIT_FUNC PyInit_calculations(void)
{
    Py_Initialize();

    return PyModule_Create(&calculations_definition);
}
