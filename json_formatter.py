import json

with open("languages/Niebla.json", "r") as file:
    data = json.load(file)

"""keys_to_delete = ["frames", "sinopsis", "observaciones", "control", "tipo"]
keys_to_delete_esc = ["codigo", "estado", "control", "tipo"]
keys_to_delete_textos = ["test", "ancho", "posicion", "titulo"]
keys_to_delete_enlaces = ["ancho", "extra", "frame", "destinoFallo", "posicion", "siempreVisible", "test"]
keys_to_delete_consecuencias = ["control", "especial", "enlaceId", "textoId", "descripcion", "escenaCodigo", "slug", "orden", "accion", "tipo", "tipoId", "escenaId"]
keys_to_delete_condiciones = ["control", "enlaceId", "textoId", "descripcion", "escenaCodigo", "slug", "tipo", "tipoId", "escenaId", "valor"]
keys_to_delete_enl_cond = ["control",  "enlaceId", "textoId", "descripcion", "escenaCodigo", "slug", "tipo", "tipoId", "escenaId", "valor"]
keys_to_delete_enl_cons = ["control", "especial", "enlaceId", "textoId", "descripcion", "escenaCodigo", "slug", "orden", "accion", "tipo", "tipoId", "escenaId"]

data = {key:value for key,value in data.items() if key not in keys_to_delete}

data["escenas"] = [
    {
        **{k: v for k, v in escena.items()
           if k not in keys_to_delete_esc and k not in ("textos", "enlaces")},

        "textos": [
            {
                **{k: v for k, v in texto.items()
                   if k not in keys_to_delete_textos and k != "enlaces"},

                "enlaces": [
                    {k: v for k, v in enlace.items()
                     if k not in keys_to_delete_enlaces}
                    for enlace in texto["enlaces"]
                ],
                "consecuencias": [
                    {k: v for k, v in consecuencia.items()
                     if k not in keys_to_delete_consecuencias}
                    for consecuencia in texto["consecuencias"]
                ],

                "condiciones": [
                    {k: v for k, v in condicion.items()
                     if k not in keys_to_delete_condiciones}
                    for condicion in texto["condiciones"]
                ]
            }
            for texto in escena.get("textos", [])
        ]
    }
    for escena in data.get("escenas", [])
]


for escena in data["escenas"]:
    for texto in escena["textos"]:
        for enlace in texto["enlaces"]:
            enlace["condiciones"] = [
                {k: v for k, v in cond.items() if k not in keys_to_delete_enl_cond}
                for cond in enlace["condiciones"]
            ]

            enlace["consecuencias"] = [
                {k: v for k, v in cons.items() if k not in keys_to_delete_enl_cons}
                for cons in enlace["consecuencias"]
            ]"""

for scene in data["scenes"]:
    scene["location"] = "bones"

with open("languages/Niebla.json", "w") as file2:
    json.dump(data, file2, indent=4)