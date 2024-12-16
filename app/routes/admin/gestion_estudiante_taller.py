from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from app.models import Estudiantes, Taller, EstudianteTaller
from app.extensions import db
from app.routes.admin.decorators import admin_required
from app.forms import EstudianteTallerForm

# Crear Blueprint
estudiantes_taller_bp = Blueprint('estudiantes_taller_admin', __name__)

# Ruta principal para gestionar estudiantes
@estudiantes_taller_bp.route('/', methods=['GET', 'POST'], endpoint='estudiantes_taller_admin_gestionar')
@login_required
@admin_required
def gestionar_estudiantes_taller():
    form = EstudianteTallerForm()

    if request.method == 'POST':
        taller_id = request.form.get('taller_id')
        id_estudiantes = request.form.getlist('id_estudiantes[]')

        if not taller_id or not id_estudiantes:
            flash('Debe seleccionar un taller y al menos un estudiante.', 'warning')
            return redirect(url_for('admin.estudiantes_taller_admin.estudiantes_taller_admin_gestionar'))

        for id_estudiante in id_estudiantes:
            asignacion_existente = EstudianteTaller.query.filter_by(
                id_estudiante=id_estudiante, taller_id=taller_id
            ).first()
            if not asignacion_existente:
                nueva_asignacion = EstudianteTaller(
                    id_estudiante=id_estudiante, taller_id=taller_id
                )
                db.session.add(nueva_asignacion)

        db.session.commit()
        flash('Estudiantes asignados correctamente al taller.', 'success')
        return redirect(url_for('admin.estudiantes_taller_admin.estudiantes_taller_admin_gestionar'))

    estudiantes = Estudiantes.query.all()
    talleres = Taller.query.all()
    return render_template('admin/estudiantes_taller.html', estudiantes=estudiantes, talleres=talleres, form=form)

# Ruta para cargar estudiantes asignados a un taller
@estudiantes_taller_bp.route('/load_students/<int:taller_id>', methods=['GET'])
@login_required
@admin_required
def load_students(taller_id):
    # Obtener estudiantes asignados al taller
    asignaciones = EstudianteTaller.query.filter_by(taller_id=taller_id).all()
    estudiantes_asignados = [asignacion.estudiante for asignacion in asignaciones]

    return render_template(
        'admin/estudiantes_list.html',
        estudiantes_asignados=estudiantes_asignados
    )



@estudiantes_taller_bp.route('/delete/<int:id_estudiante>/<int:taller_id>', methods=['POST'])
@login_required
@admin_required
def delete_asignacion(id_estudiante, taller_id):
    asignacion = EstudianteTaller.query.filter_by(
        id_estudiante=id_estudiante, taller_id=taller_id
    ).first_or_404()

    db.session.delete(asignacion)
    db.session.commit()
    flash('Asignación eliminada correctamente.', 'success')
    return '', 204
