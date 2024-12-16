from flask import Blueprint, render_template, request, redirect, flash, url_for
from flask_login import login_required, current_user
from app.models import Planificacion, Taller
from app.forms import PlanificacionForm
from app.extensions import db

# Crear el Blueprint para las rutas de Planificación para el Docente
docente_planificaciones_bp = Blueprint('docente_planificaciones', __name__, url_prefix='/docente/planificaciones')

# Ruta para listar las planificaciones del docente
@docente_planificaciones_bp.route('/', methods=['GET'])
@login_required
def listar_planificaciones_docente():
    talleres = Taller.query.filter_by(id_docente=current_user.id_docente).all()

    if not talleres:
        flash('No tienes talleres asignados.')
        return redirect(url_for('docente.dashboard'))

    # Seleccionar el primer taller por defecto
    taller_seleccionado = talleres[0]
    return redirect(url_for('docente.docente_planificaciones.ver_planificaciones_taller', taller_id=taller_seleccionado.taller_id))


# Ruta para ver planificaciones por taller
@docente_planificaciones_bp.route('/taller/<int:taller_id>', methods=['GET'])
@login_required
def ver_planificaciones_taller(taller_id):
    talleres = Taller.query.filter_by(id_docente=current_user.id_docente).all()
    taller_seleccionado = Taller.query.get_or_404(taller_id)

    # Validar que el taller pertenece al docente
    if taller_seleccionado.id_docente != current_user.id_docente:
        flash('No tienes permiso para ver este taller.')
        return redirect(url_for('docente.docente_planificaciones.listar_planificaciones_docente'))

    # Obtener planificaciones por mes
    planificaciones_por_mes = obtener_planificaciones_por_mes(taller_id)

    # Determinar el próximo mes disponible
    meses = ["marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
    siguiente_mes = next((mes for mes in meses if mes not in planificaciones_por_mes), None)

    return render_template(
        'user/gestionar_planificaciones_docente.html',
        talleres=talleres,
        taller_seleccionado=taller_seleccionado,
        planificaciones_por_mes=planificaciones_por_mes,
        siguiente_mes=siguiente_mes,
        puede_crear=bool(siguiente_mes),
        form=PlanificacionForm()
    )

# Ruta para crear planificación
@docente_planificaciones_bp.route('/crear', methods=['POST'])
@login_required
def crear_planificacion():
    taller_id = request.form['taller_id']
    form = PlanificacionForm()

    # Validar permisos
    taller = Taller.query.get_or_404(taller_id)
    if taller.id_docente != current_user.id_docente:
        flash('No tienes permiso para modificar este taller.')
        return redirect(url_for('docente.docente_planificaciones.listar_planificaciones_docente'))

    nueva_planificacion = Planificacion(
        taller_id=taller_id,
        mes=request.form['mes'],
        habilidades=form.habilidades.data,
        recursos=form.recursos.data,
        actividades=form.actividades.data,
        estado=form.estado.data
    )

    db.session.add(nueva_planificacion)
    db.session.commit()
    flash('Planificación creada exitosamente.')
    return redirect(url_for('docente.docente_planificaciones.ver_planificaciones_taller', taller_id=taller_id))

# Ruta para editar planificación
@docente_planificaciones_bp.route('/editar_planificacion', methods=['POST'])
@login_required
def editar_planificacion():
    id_planificacion = request.form.get('id_planificacion')
    habilidades = request.form.get('habilidades')
    recursos = request.form.get('recursos')
    actividades = request.form.get('actividades')
    estado = request.form.get('estado')
    
    # Buscar la planificación
    planificacion = Planificacion.query.get_or_404(id_planificacion)
    planificacion.habilidades = habilidades
    planificacion.recursos = recursos
    planificacion.actividades = actividades
    planificacion.estado = estado

    db.session.commit()
    flash('Planificación actualizada exitosamente.', 'success')
    
    return redirect(url_for('docente.docente_planificaciones.ver_planificaciones_taller', taller_id=planificacion.taller_id))

# Función auxiliar
def obtener_planificaciones_por_mes(taller_id):
    planificaciones = Planificacion.query.filter_by(taller_id=taller_id).all()
    return {plan.mes: plan for plan in planificaciones}
