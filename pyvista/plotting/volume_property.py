"""Wrapper for :vtk:`vtkVolumeProperty`."""

from __future__ import annotations

from typing import ClassVar
import weakref

import pyvista
from pyvista._deprecate_positional_args import _deprecate_positional_args
from pyvista.core.utilities.misc import no_new_attr

from . import _vtk


@no_new_attr
class VolumeProperty(_vtk.DisableVtkSnakeCase, _vtk.vtkVolumeProperty):
    """Wrap the VTK class :vtk:`vtkVolumeProperty`.

    This class is used to represent common properties associated with volume
    rendering. This includes properties for determining the type of
    interpolation to use when sampling a volume, the color of a volume, the
    scalar opacity of a volume, the gradient opacity of a volume, and the
    shading parameters of a volume.

    Parameters
    ----------
    lookup_table : pyvista.LookupTable, optional
        Lookup table to set the color and opacity transfer functions.

    interpolation_type : str, optional
        Value must be either ``'linear'`` or ``'nearest'``.

    ambient : float, optional
        When lighting is enabled, this is the amount of light in
        the range of 0 to 1 (default 0.0) that reaches the actor
        when not directed at the light source emitted from the
        viewer.

    diffuse : float, optional
        The diffuse lighting coefficient.

    specular : float, optional
        The specular lighting coefficient.

    specular_power : float, optional
        The specular power. Between 0.0 and 128.0.

    shade : bool, optional
        Enable or disable volume shading.  If shading is turned off, then the
        mapper for the volume will not perform shading calculations. If shading
        is turned on, the mapper may perform shading calculations - in some
        cases shading does not apply (for example, in a maximum intensity
        projection) and therefore shading will not be performed even if this
        flag is on. For a compositing type of mapper, turning shading off is
        generally the same as setting ``ambient=1``, ``diffuse=0``,
        ``specular=0``. Shading can be independently turned on/off per
        component.

    opacity_unit_distance : float, optional
        This is the unit distance on which the scalar opacity transfer function
        is defined. By default this is 1.0, meaning that over a distance of 1.0
        units, a given opacity (from the transfer function) is
        accumulated. This is adjusted for the actual sampling distance during
        rendering.

    Examples
    --------
    Create a sample dataset from perlin noise and apply a lookup table to the
    :class:`VolumeProperty`.

    >>> import pyvista as pv
    >>> noise = pv.perlin_noise(1, (1, 3, 5), (0, 0, 0))
    >>> grid = pv.sample_function(
    ...     noise, bounds=[0, 3.0, -0, 1.0, 0, 1.0], dim=(40, 40, 40)
    ... )
    >>> pl = pv.Plotter()
    >>> actor = pl.add_volume(grid, show_scalar_bar=False)
    >>> lut = actor.mapper.lookup_table
    >>> lut.cmap = 'bwr'
    >>> lut.apply_opacity([1.0, 0.0, 0.0, 0.3, 0.0, 0.0, 0.0, 0.3])
    >>> pl.show()

    """

    _new_attr_exceptions: ClassVar[list[str]] = ['_lookup_table_', '_lookup_table_observer_id']

    @_deprecate_positional_args
    def __init__(  # noqa: PLR0917
        self,
        lookup_table=None,
        interpolation_type=None,
        ambient=None,
        diffuse=None,
        specular=None,
        specular_power=None,
        shade=None,
        opacity_unit_distance=None,
    ):
        """Initialize the :vtk:`vtkVolumeProperty` class."""
        super().__init__()
        self._lookup_table_ = None
        self._lookup_table_observer_id = None
        if lookup_table is not None:
            self.apply_lookup_table(lookup_table)
        if interpolation_type is not None:
            self.interpolation_type = interpolation_type
        if ambient is not None:
            self.ambient = ambient
        if diffuse is not None:
            self.diffuse = diffuse
        if specular is not None:
            self.specular = specular
        if specular_power is not None:
            self.specular_power = specular_power
        if shade is not None:
            self.shade = shade
        if opacity_unit_distance is not None:
            self.opacity_unit_distance = opacity_unit_distance

    @property
    def _lookup_table(self) -> pyvista.LookupTable | None:
        """Get the lookup table if applied via apply_lookup_table."""
        if self._lookup_table_ is not None:
            return self._lookup_table_()
        return None

    @_lookup_table.setter
    def _lookup_table(self, lookup_table: pyvista.LookupTable):
        """Set the lookup table if applied via apply_lookup_table."""
        if self._lookup_table is not None and self._lookup_table_observer_id is not None:
            # Clean up the old lookup table observer
            self._lookup_table.RemoveObserver(self._lookup_table_observer_id)
            self._lookup_table_observer_id = None
        self._lookup_table_ = weakref.ref(lookup_table)
        self._lookup_table_observer_id = lookup_table.AddObserver(
            _vtk.vtkCommand.ModifiedEvent,
            lambda *_: self.reapply_lookup_table(),
        )

    def reapply_lookup_table(self):
        """Reapply the lookup table previously applied.

        The VolumeProperty is unable to keep a dynamic link to the colors
        and mapping laid out in the lookup table. This method allows you to
        reapply the lookup table to the VolumeProperty. This is useful if
        you modify the lookup table after it is applied to the
        VolumeProperty.

        We have our own modified event observer to reapply this automatically
        when the lookup table is modified.

        """
        if self._lookup_table is not None:
            self.apply_lookup_table(self._lookup_table)

    def apply_lookup_table(self, lookup_table: pyvista.LookupTable):
        """Apply a lookup table to the volume property.

        Applies both the color and opacity of the lookup table as transfer
        functions.

        Parameters
        ----------
        lookup_table : pyvista.LookupTable, optional
            Lookup table to set the color and opacity transfer functions.

        Examples
        --------
        Plot perlin noise volumetrically using a custom lookup table.

        >>> import pyvista as pv
        >>> noise = pv.perlin_noise(1, (1, 3, 5), (0, 0, 0))
        >>> grid = pv.sample_function(
        ...     noise, bounds=[0, 3.0, -0, 1.0, 0, 1.0], dim=(40, 40, 40)
        ... )
        >>> pl = pv.Plotter()
        >>> actor = pl.add_volume(grid, show_scalar_bar=False)
        >>> lut = actor.mapper.lookup_table
        >>> lut.cmap = 'bwr'
        >>> lut.apply_opacity([1.0, 0.0, 0.0, 0.3, 0.0, 0.0, 0.0, 0.3])
        >>> pl.show()

        """
        if not isinstance(lookup_table, pyvista.LookupTable):
            msg = '`lookup_table` must be a `pyvista.LookupTable`'
            raise TypeError(msg)
        if self._lookup_table != lookup_table:
            self._lookup_table = lookup_table
        self.SetColor(lookup_table.to_color_tf())
        self.SetScalarOpacity(lookup_table.to_opacity_tf())

    def __del__(self):
        """Clean up the lookup table observer when the object is deleted."""
        if self._lookup_table_observer_id is not None and self._lookup_table is not None:
            self._lookup_table.RemoveObserver(self._lookup_table_observer_id)
            self._lookup_table_observer_id = None
        self._lookup_table_ = None

    @property
    def interpolation_type(self) -> str:  # numpydoc ignore=RT01
        """Return or set the interpolation type.

        Value must be either ``'linear'`` or ``'nearest'``.

        Examples
        --------
        Create a sample :class:`pyvista.ImageData` dataset.

        >>> import numpy as np
        >>> import pyvista as pv
        >>> n = 21
        >>> c = -(n - 1) / 2
        >>> vol = pv.ImageData(dimensions=(n, n, n), origin=(c, c, c))
        >>> scalars = np.linalg.norm(vol.points, axis=1)
        >>> scalars *= 255 / scalars.max()
        >>> vol['scalars'] = scalars

        Demonstrate nearest (default) interpolation.

        >>> pl = pv.Plotter()
        >>> actor = pl.add_volume(
        ...     vol,
        ...     show_scalar_bar=False,
        ...     opacity=[0.3, 0.0, 0.05, 0.0, 0.0, 0.0, 1.0, 0.0],
        ...     cmap='plasma',
        ... )
        >>> actor.prop.interpolation_type = 'nearest'
        >>> pl.show()

        Demonstrate linear interpolation.

        >>> pl = pv.Plotter()
        >>> actor = pl.add_volume(
        ...     vol,
        ...     show_scalar_bar=False,
        ...     opacity=[0.3, 0.0, 0.05, 0.0, 0.0, 0.0, 1.0, 0.0],
        ...     cmap='plasma',
        ... )
        >>> actor.prop.interpolation_type = 'linear'
        >>> pl.show()

        """
        return self.GetInterpolationTypeAsString().split()[0].lower()

    @interpolation_type.setter
    def interpolation_type(self, value: str):
        if value == 'linear':
            self.SetInterpolationTypeToLinear()
        elif value == 'nearest':
            self.SetInterpolationTypeToNearest()
        else:
            msg = '`interpolation_type` must be either "linear" or "nearest"'
            raise ValueError(msg)

    @property
    def opacity_unit_distance(self) -> float:  # numpydoc ignore=RT01
        """Return or set the opacity unit distance.

        This is the unit distance on which the scalar opacity transfer function
        is defined.

        By default this is 1.0, meaning that over a distance of 1.0 units, a
        given opacity (from the transfer function) is accumulated. This is
        adjusted for the actual sampling distance during rendering.
        """
        return self.GetScalarOpacityUnitDistance()

    @opacity_unit_distance.setter
    def opacity_unit_distance(self, value: float):
        self.SetScalarOpacityUnitDistance(value)

    @property
    def shade(self) -> bool:  # numpydoc ignore=RT01
        """Return or set shading of a volume.

        If shading is turned off, then the mapper for the volume will not
        perform shading calculations. If shading is turned on, the mapper may
        perform shading calculations - in some cases shading does not apply
        (for example, in a maximum intensity projection) and therefore shading
        will not be performed even if this flag is on. For a compositing type
        of mapper, turning shading off is generally the same as setting
        ``ambient=1``, ``diffuse=0``, ``specular=0``. Shading can be
        independently turned on/off per component.

        """
        return bool(self.GetShade())

    @shade.setter
    def shade(self, value: bool):
        self.SetShade(value)

    @property
    def independent_components(self) -> bool:  # numpydoc ignore=RT01
        """Return or set independent components.

        If ``False``, then you must have either 2 or 4 component data.
        For 2 component data, the first is passed through the
        first color transfer function and the second component is passed
        through the first scalar opacity (and gradient opacity) transfer
        function. Normals will be generated off of the second component. When
        using gradient based opacity modulation, the gradients are computed off
        of the second component.

        For 4 component data, the first three will directly represent RGB (no
        lookup table). The fourth component will be passed through the first
        scalar opacity transfer function for opacity and first gradient opacity
        transfer function for gradient based opacity modulation. Normals will
        be generated from the fourth component. When using gradient based
        opacity modulation, the gradients are computed off of the fourth
        component.
        """
        return bool(self.GetIndependentComponents())

    @independent_components.setter
    def independent_components(self, value: bool):
        self.SetIndependentComponents(value)

    @property
    def ambient(self) -> float:  # numpydoc ignore=RT01
        """Return or set ambient lighting coefficient.

        This is the amount of light in the range of 0 to 1 (default 0.0) that
        reaches the actor when not directed at the light source emitted from
        the viewer.

        Changing attribute has no effect unless :attr:`VolumeProperty.shade` is
        set to ``True``.

        """
        return self.GetAmbient()

    @ambient.setter
    def ambient(self, value: float):
        self.SetAmbient(value)

    @property
    def diffuse(self) -> float:  # numpydoc ignore=RT01
        """Return or set the diffuse lighting coefficient.

        This is the scattering of light by reflection or transmission. Diffuse
        reflection results when light strikes an irregular surface such as a
        frosted window or the surface of a frosted or coated light bulb.

        Changing attribute has no effect unless :attr:`VolumeProperty.shade` is
        set to ``True``.

        """
        return self.GetDiffuse()

    @diffuse.setter
    def diffuse(self, value: float):
        self.SetDiffuse(value)

    @property
    def specular(self) -> float:  # numpydoc ignore=RT01
        """Return or set specular.

        Default 0.0

        Specular lighting simulates the bright spot of a light that appears on
        shiny objects.

        Changing attribute has no effect unless :attr:`VolumeProperty.shade` is
        set to ``True``.

        """
        return self.GetSpecular()

    @specular.setter
    def specular(self, value: float):
        self.SetSpecular(value)

    @property
    def specular_power(self) -> float:  # numpydoc ignore=RT01
        """Return or set specular power.

        The specular power. Between 0.0 and 128.0. Default 10.0

        """
        return self.GetSpecularPower()

    @specular_power.setter
    def specular_power(self, value: float):
        self.SetSpecularPower(value)

    def copy(self) -> VolumeProperty:
        """Create a deep copy of this property.

        Returns
        -------
        pyvista.plotting.volume_property.VolumeProperty
            Deep copy of this property.

        """
        new_prop = VolumeProperty()
        new_prop.DeepCopy(self)
        return new_prop

    def __repr__(self):
        """Representation of this property."""
        props = [
            f'{type(self).__name__} ({hex(id(self))})',
        ]

        for attr in dir(self):
            if not attr.startswith('_') and attr[0].islower():
                name = ' '.join(attr.split('_')).capitalize() + ':'
                try:
                    value = getattr(self, attr)
                except AttributeError:  # pragma:no cover
                    continue
                if callable(value):
                    continue
                if isinstance(value, str):
                    value = f'"{value}"'
                props.append(f'  {name:28s} {value}')

        return '\n'.join(props)
