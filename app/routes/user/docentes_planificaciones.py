from flask import Blueprint, render_template, request, redirect, flash, url_for
from flask_login import login_required, current_user
from app.models import Planificacion, Taller
from app.forms import PlanificacionForm
from app.extensions import db

# Crear el Blueprint para las rutas de Planificación para el Docente
docente_planificaciones_bp = Blueprint('docente_planificaciones', __name__, url_prefix='/docente/planificaciones')

# Ruta para listar las planificaciones del docente (solo los talleres asignados al docente)
@docente_planificaciones_bp.route('/', methods=['GET'])
@login_required
def listar_planificaciones_docente():
    talleres = Taller.query.filter_by(id_docente=current_user.id_docente).all()

    if not talleres:
        flash('No tienes talleres asignados para mostrar planificaciones.')
        return redirect(url_for('docente.dashboard'))  # Redirigir al Dashboard si no hay talleres

    taller_seleccionado = talleres[0]  # Seleccionar el primer taller como predeterminado

    # Obtener las planificaciones del taller seleccionado
    planificaciones = Planificacion.query.filter_by(taller_id=taller_seleccionado.taller_id).all()

    # Listado de meses
    meses = ["marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]

    # Diccionario para almacenar las planificaciones por mes
    planificaciones_por_mes = {mes: None for mes in meses}

    # Llenar el diccionario con las planificaciones existentes
    for plan in planificaciones:
        planificaciones_por_mes[plan.mes] = plan

    # Determinar si se puede crear una nueva planificación
    siguiente_mes = None
    puede_crear = True
    for i, mes in enumerate(meses):
        if planificaciones_por_mes[mes] is None:
            siguiente_mes = mes
            if i > 0 and planificaciones_por_mes[meses[i - 1]] is None:
                puede_crear = False
            break

    return render_template(
        'user/gestionar_planificaciones_docente.html',
        talleres=talleres,
        taller_seleccionado=taller_seleccionado,
        planificaciones_por_mes=planificaciones_por_mes,
        siguiente_mes=siguiente_mes,
        puede_crear=puede_crear,
        form=PlanificacionForm()  # Asegúrate de pasar el formulario aquí
    )


# Función para obtener las planificaciones por mes
def obtener_planificaciones_por_mes(taller_id):
    # Consultar las planificaciones del taller específico
    planificaciones = Planificacion.query.filter_by(taller_id=taller_id).all()

    # Crear un diccionario para almacenar las planificaciones organizadas por mes
    planificaciones_por_mes = {}

    # Llenar el diccionario con los meses como claves y las planificaciones correspondientes como valores
    for plan in planificaciones:
        mes = plan.mes  # Suponiendo que la planificación tiene un atributo 'mes'
        if mes not in planificaciones_por_mes:
            planificaciones_por_mes[mes] = []
        planificaciones_por_mes[mes].append(plan)

    return planificaciones_por_mes


# Ruta para ver las planificaciones de un taller específico
@docente_planificaciones_bp.route('/planificaciones/taller/<int:taller_id>', methods=['GET'])
@login_required
def ver_planificaciones_taller(taller_id):
    # Lógica para obtener las planificaciones por taller
    talleres = Taller.query.all()  # Ejemplo, consulta de talleres
    planificaciones_por_mes = obtener_planificaciones_por_mes(taller_id)  # Función para obtener las planificaciones por mes
    return render_template('user/gestionar_planificaciones_docente.html', 
                           talleres=talleres, 
                           planificaciones_por_mes=planificaciones_por_mes, 
                           taller_seleccionado=taller_id)


# Ruta para crear una nueva planificación para un taller
@docente_planificaciones_bp.route('/crear_planificacion', methods=['POST'])
@login_required
def crear_planificacion():
    taller_id = request.form['taller_id']
    form = PlanificacionForm()

    taller = Taller.query.get_or_404(taller_id)
    if taller.id_docente != current_user.id_docente:
        flash('No tienes acceso para crear una planificación para este taller.')
        return redirect(url_for('docente_planificaciones.ver_planificaciones_taller', taller_id=taller_id))

    nueva_planificacion = Planificacion(
        taller_id=taller_id,
        mes=form.mes.data,
        habilidades=form.habilidades.data,
        recursos=form.recursos.data,
        actividades=form.actividades.data,
        estado=form.estado.data
    )

    db.session.add(nueva_planificacion)
    db.session.commit()
    flash('Planificación creada exitosamente.')

    return redirect(url_for('docente_planificaciones.ver_planificaciones_taller', taller_id=taller_id))


# Ruta para actualizar el objetivo general
@docente_planificaciones_bp.route('/actualizar_objetivo_general', methods=['POST'])
@login_required
def actualizar_objetivo_general():
    taller_id = request.form['taller_id']
    taller = Taller.query.get_or_404(taller_id)

    objetivo_general = request.form['objetivo_general']
    taller.objetivo_general = objetivo_general

    db.session.commit()
    flash('Objetivo general actualizado exitosamente.')

    return redirect(url_for('docente_planificaciones.listar_planificaciones_docente'))


# Ruta para editar planificación
@docente_planificaciones_bp.route('/planificaciones/editar_planificacion', methods=['POST'])
@login_required
def editar_planificacion():
    # Lógica para editar una planificación
    id_planificacion = request.form.get('id_planificacion')
    habilidades = request.form.get('habilidades')
    recursos = request.form.get('recursos')
    actividades = request.form.get('actividades')
    estado = request.form.get('estado')
    
    planificacion = Planificacion.query.get(id_planificacion)
    planificacion.habilidades = habilidades
    planificacion.recursos = recursos
    planificacion.actividades = actividades
    planificacion.estado = estado
    db.session.commit()
    return redirect(url_for('docente_planificaciones.ver_planificaciones_taller', taller_id=planificacion.taller_id))
