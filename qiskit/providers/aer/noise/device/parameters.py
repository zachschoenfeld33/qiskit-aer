# This code is part of Qiskit.
#
# (C) Copyright IBM 2018, 2019.
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE.txt file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.

"""
Functions to extract device error parameters from backend properties.
"""

from numpy import inf

# Time and frequency unit conversions
_MICROSECOND_UNITS = {'s': 1e6, 'ms': 1e3, 'µs': 1, 'us': 1, 'ns': 1e-3}
_NANOSECOND_UNITS = {'s': 1e9, 'ms': 1e6, 'µs': 1e3, 'us': 1e3, 'ns': 1}
_GHZ_UNITS = {'Hz': 1e-9, 'KHz': 1e-6, 'MHz': 1e-3, 'GHz': 1, 'THz': 1e3}


def gate_param_values(properties):
    """Get gate error values for backend gate from backend properties

    Args:
        properties (BackendProperties): device backend properties

    Returns:
        list: A list of tuples (name, qubits, time, error). If gate
              error or gate_length information is not available None
              will be returned for value.
    """
    values = []
    for gate in properties.gates:
        name = gate.gate
        qubits = gate.qubits
        # Check for gate time information
        gate_length = None  # default value
        time_param = _check_for_item(gate.parameters, 'gate_length')
        if hasattr(time_param, 'value'):
            gate_length = time_param.value
            if hasattr(time_param, 'unit'):
                # Convert gate time to ns
                gate_length *= _NANOSECOND_UNITS.get(time_param.unit, 1)
        # Check for gate error information
        gate_error = None  # default value
        error_param = _check_for_item(gate.parameters, 'gate_error')
        if hasattr(error_param, 'value'):
            gate_error = error_param.value
        values.append((name, qubits, gate_length, gate_error))

    return values


def gate_error_values(properties):
    """Get gate error values for backend gate from backend properties

    Args:
        properties (BackendProperties): device backend properties

    Returns:
        list: A list of tuples (name, qubits, value). If gate
              error information is not available None will be returned for
              value.
    """
    values = []
    for gate in properties.gates:
        name = gate.gate
        qubits = gate.qubits
        value = None  # default value
        params = _check_for_item(gate.parameters, 'gate_error')
        if hasattr(params, 'value'):
            value = params.value
        values.append((name, qubits, value))
    return values


def gate_length_values(properties):
    """Get gate length values for backend gate from backend properties

    Gate length values are returned in nanosecond (ns) units.

    Args:
        properties (BackendProperties): device backend properties

    Returns:
        list: A list of tuples (name, qubits, value). If gate
              time information is not available None will be returned for
              value.
    """
    values = []
    for gate in properties.gates:
        name = gate.gate
        qubits = gate.qubits
        value = None  # default value
        params = _check_for_item(gate.parameters, 'gate_length')
        if hasattr(params, 'value'):
            value = params.value
            if hasattr(params, 'unit'):
                # Convert gate time to ns
                value *= _NANOSECOND_UNITS.get(params.unit, 1)
        values.append((name, qubits, value))
    return values


def readout_error_values(properties):
    """Get readout error values for each qubit from backend properties

    Args:
        properties (BackendProperties): device backend properties

    Returns:
        list: A list of readout error values for qubits. If readout
              error information is not available None will be returned
              for value.
    """
    values = []
    for qubit_props in properties.qubits:
        value = None  # default value
        params = _check_for_item(qubit_props, 'readout_error')
        if hasattr(params, 'value'):
            value = params.value
        values.append(value)
    return values


def thermal_relaxation_values(properties):
    """Return list of T1, T2 and frequency values from backend properties.

    T1 and T2 values are returned in microsecond (µs) units.
    Frequency is returned in gigahertz (GHz) units.

    Args:
        properties (BackendProperties): device backend properties

    Returns:
        list: A list of tuples (T1, T2, freq) for each qubit in the device
        where T1 and T2 are in microsecond units, and frequency is in GHz.
        If T1, T2, of frequency cannot be loaded for qubit a value of
        Numpy.inf will be used.
    """
    values = []
    for qubit_props in properties.qubits:
        # pylint: disable=invalid-name
        # Default values
        t1, t2, freq = inf, inf, inf

        # Get the readout error value
        t1_params = _check_for_item(qubit_props, 'T1')
        t2_params = _check_for_item(qubit_props, 'T2')
        freq_params = _check_for_item(qubit_props, 'frequency')

        # Load values from parameters
        if hasattr(t1_params, 'value'):
            t1 = t1_params.value
            if hasattr(t1_params, 'unit'):
                # Convert to micro seconds
                t1 *= _MICROSECOND_UNITS.get(t1_params.unit, 1)
        if hasattr(t2_params, 'value'):
            t2 = t2_params.value
            if hasattr(t2_params, 'unit'):
                # Convert to micro seconds
                t2 *= _MICROSECOND_UNITS.get(t2_params.unit, 1)
        if hasattr(t2_params, 'value'):
            freq = freq_params.value
            if hasattr(freq_params, 'unit'):
                # Convert to Gigahertz
                freq *= _GHZ_UNITS.get(freq_params.unit, 1)

        # NOTE: T2 cannot be larged than 2 * T1 for a physical noise
        # channel, however if a backend eroneously reports such a value we
        # truncated it here:
        t2 = min(2 * t1, t2)

        values.append((t1, t2, freq))
    return values


def _check_for_item(lst, name):
    """Search list for item with given name."""
    filtered = [item for item in lst if item.name == name]
    if not filtered:
        return None
    else:
        return filtered[0]
