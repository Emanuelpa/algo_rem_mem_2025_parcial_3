#!/usr/bin/env python

from collections import deque

marcos_libres = [0x0,0x1,0x2]
reqs = [ 0x00, 0x12, 0x64, 0x65, 0x8D, 0x8F, 0x19, 0x18, 0xF1, 0x0B, 0xDF, 0x0A ]
segmentos =[ ('.text', 0x00, 0x1A),
             ('.data', 0x40, 0x28),
             ('.heap', 0x80, 0x1F),
             ('.stack', 0xC0, 0x22),
            ]

def procesar(segmentos, reqs, marcos_libres):
    retorno = []

    if not isinstance(segmentos, list) or not all(isinstance(s, tuple) and len(s) == 3 for s in segmentos):
        raise ValueError("Segmentos debe ser una lista de tuplas (nombre, base, limite)")

    if not isinstance(reqs, list) or not all(isinstance(r, int) and r >= 0 for r in reqs):
        raise ValueError("Reqs debe ser una lista de enteros no negativos")

    if not isinstance(marcos_libres, list) or not all(isinstance(m, int) and m >= 0 for m in marcos_libres):
        raise ValueError("Marcos libres debe ser una lista de enteros no negativos")

    if len(set(marcos_libres)) != len(marcos_libres):
        raise ValueError("Los marcos libres no deben estar repetidos")

    if not segmentos:
        raise ValueError("Debe haber al menos un segmento definido")

    if not reqs:
        return retorno


    tabla_paginas = {}
    cola = deque(maxlen=3)

    for req in reqs:
        pertence_segmento = None
        for segmento, base, limite in segmentos:
            if req >= base and req < base + limite:
                pertence_segmento = (segmento, base)
                break
        
        if pertence_segmento is None:
            retorno.append((req, 0x1ff, "Segmentation Fault"))
            return retorno
        
        nombre, base = pertence_segmento
        relativa_segm = req - base
        pagina = relativa_segm // 16
        relativa_pag = relativa_segm % 16
        
        pagina_asignar = (nombre, pagina)
        #print("---------------------------------------------------------")
        #print("va a asignar", pagina_asignar)
        if pagina_asignar in tabla_paginas.values():
            marco = None
            for marco_, pagina_ in tabla_paginas.items():
                if pagina_ == pagina_asignar:
                    marco = marco_
            cola.remove(marco)
            cola.append(marco)
            dir_fisica = marco * 16 + relativa_pag
            retorno.append((req, dir_fisica, "Marco ya estaba asignado"))
        else:
            if marcos_libres:
                marco = marcos_libres.pop(0)
                tabla_paginas[marco] = pagina_asignar
                dir_fisica = marco * 16 + relativa_pag
                retorno.append((req, dir_fisica, "Marco libre asignado"))
                cola.append(marco)
            else:
                marco_reemplazo = cola.popleft()
                cola.append(marco_reemplazo)
                tabla_paginas[marco_reemplazo] = pagina_asignar
                dir_fisica = marco_reemplazo * 16 + relativa_pag
                retorno.append((req, dir_fisica, "Marco asignado"))
        #print(f"req{hex(req)}, tabla de paginas {tabla_paginas}, cola{cola}")
        #print("---------------------------------------------------------")
    return retorno
                
    
def print_results(results):
    for result in results:
        print(f"Req: {result[0]:#0{4}x} Direccion Fisica: {result[1]:#0{4}x} Acción: {result[2]}")

if __name__ == '__main__':
    results = procesar(segmentos, reqs, marcos_libres)
    print_results(results)

