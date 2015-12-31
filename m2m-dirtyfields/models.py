from dirtyfields import DirtyFieldsMixin


class M2MDirtyFieldsMixin(DirtyFieldsMixin):
    def __init__(self, *args, **kwargs):
        super(M2MDirtyFieldsMixin, self).__init__(*args, **kwargs)
        post_save.connect(
            reset_state, sender=self.__class__,
            dispatch_uid='{name}-DirtyFieldsMixin-sweeper'.format(
                name=self.__class__.__name__))
        reset_state(sender=self.__class__, instance=self)

    def _as_dict_m2m(self):
        if self.pk:
            m2m_fields = dict([
                (f.attname, set([
                    obj.id for obj in getattr(self, f.attname).all()
                ]))
                for f,model in self._meta.get_m2m_with_model()
            ])
            return m2m_fields
        return {}

    def get_dirty_fields(self, check_relationship=False):
        changed_fields = super(M2MDirtyFieldsMixin, self).get_dirty_fields(check_relationship)
        new_m2m_state = self._as_dict_m2m()
        changed_m2m_fields = dict([
            (key, value)
            for key, value in self._original_m2m_state.iteritems()
            if sorted(value) != sorted(new_m2m_state[key])
        ])
        changed_fields.update(changed_m2m_fields)
        return changed_fields

def reset_state(sender, instance, **kwargs):
    # original state should hold all possible dirty fields to avoid
    # getting a `KeyError` when checking if a field is dirty or not
    instance._original_state = instance._as_dict(check_relationship=True)
    instance._original_m2m_state = instance._as_dict_m2m()

