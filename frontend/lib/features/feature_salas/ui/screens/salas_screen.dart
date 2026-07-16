import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:ghorario/core/themes/app_colors.dart';
import 'package:ghorario/core/themes/app_text_styles.dart';
import 'package:ghorario/core/widgets/import_excel_button.dart';
import 'package:ghorario/features/feature_importacao/domain/entities/entidade_importacao.dart';
import 'package:ghorario/features/feature_importacao/domain/usecase/importar_excel_usecase.dart';
import 'package:ghorario/features/feature_salas/domain/entities/sala.dart';
import 'package:ghorario/features/feature_salas/presentation/controller/salas_controller.dart';
import 'package:ghorario/features/feature_salas/presentation/provider/salas_provider.dart';
import 'package:ghorario/features/feature_salas/presentation/states/salas_state.dart';

/// Screen for displaying and managing rooms/classrooms (salas).
class SalasScreen extends StatefulWidget {
  const SalasScreen({super.key});

  @override
  State<SalasScreen> createState() => _SalasScreenState();
}

class _SalasScreenState extends State<SalasScreen> {
  late final SalasController _controller;
  bool _isListView = false;

  @override
  void initState() {
    super.initState();
    _controller = SalasController(provider: context.read<SalasProvider>());
    WidgetsBinding.instance.addPostFrameCallback((_) => _controller.init());
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  String _getTipoSala(String name) {
    final lower = name.toLowerCase();
    if (lower.contains('lab') || lower.contains('laboratório')) {
      return 'LABORATÓRIO';
    } else if (lower.contains('aud') || lower.contains('auditório')) {
      return 'AUDITÓRIO';
    }
    return 'SALA DE AULA';
  }

  IconData _getIconData(String type) {
    switch (type) {
      case 'LABORATÓRIO':
        return Icons.biotech_rounded;
      case 'AUDITÓRIO':
        return Icons.campaign_rounded;
      case 'SALA DE AULA':
      default:
        return Icons.meeting_room_rounded;
    }
  }

  Color _getIconBgColor(String type) {
    switch (type) {
      case 'LABORATÓRIO':
        return const Color(0xFFE0F2FE);
      case 'AUDITÓRIO':
        return const Color(0xFFFEE2E2);
      case 'SALA DE AULA':
      default:
        return const Color(0xFFFEF3C7);
    }
  }

  Color _getIconColor(String type) {
    switch (type) {
      case 'LABORATÓRIO':
        return const Color(0xFF0284C7);
      case 'AUDITÓRIO':
        return const Color(0xFFEF4444);
      case 'SALA DE AULA':
      default:
        return const Color(0xFFD97706);
    }
  }

  void _showNewSalaBottomSheet() {
    final nameController = TextEditingController();
    final codeController = TextEditingController();
    final capacityController = TextEditingController(text: '40');
    String selectedType = 'SALA DE AULA';

    final List<String> types = ['SALA DE AULA', 'LABORATÓRIO', 'AUDITÓRIO'];

    showModalBottomSheet<void>(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.white,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (BuildContext context) {
        return StatefulBuilder(
          builder: (BuildContext context, StateSetter setModalState) {
            return Padding(
              padding: EdgeInsets.only(
                bottom: MediaQuery.of(context).viewInsets.bottom,
                left: 24,
                right: 24,
                top: 24,
              ),
              child: SingleChildScrollView(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Text(
                      'Nova Sala',
                      style: AppTextStyles.heading2.copyWith(color: AppColors.blackBlue),
                    ),
                    const SizedBox(height: 16),
                    TextField(
                      controller: nameController,
                      decoration: const InputDecoration(
                        labelText: 'Nome da Sala (Ex: Sala 204)',
                        border: OutlineInputBorder(),
                      ),
                    ),
                    const SizedBox(height: 12),
                    Row(
                      children: [
                        Expanded(
                          child: TextField(
                            controller: codeController,
                            decoration: const InputDecoration(
                              labelText: 'Código (Ex: S204)',
                              border: OutlineInputBorder(),
                            ),
                          ),
                        ),
                        const SizedBox(width: 12),
                        Expanded(
                          child: TextField(
                            controller: capacityController,
                            keyboardType: TextInputType.number,
                            decoration: const InputDecoration(
                              labelText: 'Capacidade',
                              border: OutlineInputBorder(),
                            ),
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 12),
                    DropdownButtonFormField<String>(
                      initialValue: selectedType,
                      decoration: const InputDecoration(
                        labelText: 'Tipo de Espaço',
                        border: OutlineInputBorder(),
                      ),
                      items: types.map((t) => DropdownMenuItem(value: t, child: Text(t))).toList(),
                      onChanged: (val) {
                        if (val != null) {
                          setModalState(() => selectedType = val);
                        }
                      },
                    ),
                    const SizedBox(height: 24),
                    Row(
                      mainAxisAlignment: MainAxisAlignment.end,
                      children: [
                        TextButton(
                          onPressed: () => Navigator.pop(context),
                          child: const Text('Cancelar', style: TextStyle(color: AppColors.textSecondary)),
                        ),
                        const SizedBox(width: 8),
                        ElevatedButton(
                          style: ElevatedButton.styleFrom(
                            backgroundColor: AppColors.blackBlue,
                            foregroundColor: Colors.white,
                            shape: RoundedRectangleBorder(
                              borderRadius: BorderRadius.circular(8),
                            ),
                          ),
                          onPressed: () async {
                            if (nameController.text.isEmpty || codeController.text.isEmpty) return;
                            String finalName = nameController.text;
                            if (selectedType == 'LABORATÓRIO' && !finalName.toLowerCase().contains('lab')) {
                              finalName = 'Lab $finalName';
                            } else if (selectedType == 'AUDITÓRIO' && !finalName.toLowerCase().contains('aud')) {
                              finalName = 'Aud $finalName';
                            }

                            final newSala = Sala(
                              id: '',
                              name: finalName,
                              code: codeController.text.toUpperCase(),
                              capacity: int.tryParse(capacityController.text) ?? 40,
                            );
                            final navigator = Navigator.of(context);
                            final messenger = ScaffoldMessenger.of(context);
                            final success = await _controller.addSala(newSala);
                            if (success) {
                              navigator.pop();
                            } else {
                              messenger.showSnackBar(
                                SnackBar(content: Text(_controller.value.errorMessage ?? 'Erro ao criar sala.')),
                              );
                            }
                          },
                          child: const Text('Adicionar'),
                        ),
                      ],
                    ),
                    const SizedBox(height: 24),
                  ],
                ),
              ),
            );
          },
        );
      },
    );
  }

  Widget _buildViewToggle() {
    return Container(
      decoration: BoxDecoration(
        border: Border.all(color: const Color(0xFFE2E8F0), width: 1.2),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          IconButton(
            icon: const Icon(Icons.grid_view_rounded, size: 20),
            color: _isListView ? const Color(0xFF94A3B8) : AppColors.blackBlue,
            tooltip: 'Grelha',
            onPressed: () => setState(() => _isListView = false),
          ),
          IconButton(
            icon: const Icon(Icons.view_list_rounded, size: 20),
            color: _isListView ? AppColors.blackBlue : const Color(0xFF94A3B8),
            tooltip: 'Lista',
            onPressed: () => setState(() => _isListView = true),
          ),
        ],
      ),
    );
  }

  Widget _buildListView(List<Sala> salas) {
    return Container(
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: const Color(0xFFE8EEF5), width: 1.2),
      ),
      clipBehavior: Clip.antiAlias,
      child: Column(
        children: [
          const Padding(
            padding: EdgeInsets.symmetric(horizontal: 24, vertical: 12),
            child: Row(
              children: [
                Expanded(flex: 2, child: Text('CÓDIGO', style: TextStyle(fontSize: 11, fontWeight: FontWeight.bold, color: Color(0xFF94A3B8), letterSpacing: 0.8, fontFamily: 'Poppins'))),
                Expanded(flex: 5, child: Text('NOME', style: TextStyle(fontSize: 11, fontWeight: FontWeight.bold, color: Color(0xFF94A3B8), letterSpacing: 0.8, fontFamily: 'Poppins'))),
                Expanded(flex: 2, child: Text('CAPACIDADE', style: TextStyle(fontSize: 11, fontWeight: FontWeight.bold, color: Color(0xFF94A3B8), letterSpacing: 0.8, fontFamily: 'Poppins'))),
              ],
            ),
          ),
          const Divider(color: Color(0xFFF1F5F9), height: 1, thickness: 1),
          Expanded(
            child: ListView.separated(
              padding: EdgeInsets.zero,
              itemCount: salas.length,
              separatorBuilder: (context, index) => const Divider(color: Color(0xFFF1F5F9), height: 1, thickness: 1),
              itemBuilder: (context, index) {
                final sala = salas[index];
                return Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 16),
                  child: Row(
                    children: [
                      Expanded(flex: 2, child: Text(sala.code ?? 'N/A', style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w600, color: AppColors.blackBlue, fontFamily: 'Poppins'))),
                      Expanded(flex: 5, child: Text(sala.name, style: const TextStyle(fontSize: 14, fontWeight: FontWeight.bold, color: AppColors.blackBlue, fontFamily: 'Poppins'))),
                      Expanded(flex: 2, child: Text('${sala.capacity ?? 0}', style: const TextStyle(fontSize: 14, color: AppColors.lightBlue, fontWeight: FontWeight.bold, fontFamily: 'Poppins'))),
                    ],
                  ),
                );
              },
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildGridView(List<Sala> salas) {
    return GridView.builder(
      padding: EdgeInsets.zero,
      gridDelegate: const SliverGridDelegateWithMaxCrossAxisExtent(
        maxCrossAxisExtent: 280,
        mainAxisExtent: 180,
        crossAxisSpacing: 24,
        mainAxisSpacing: 24,
      ),
      itemCount: salas.length,
      itemBuilder: (context, index) {
        final sala = salas[index];
        final tipo = _getTipoSala(sala.name);
        final iconBg = _getIconBgColor(tipo);
        final iconCol = _getIconColor(tipo);
        final iconData = _getIconData(tipo);

        return Container(
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(16),
            border: Border.all(color: const Color(0xFFE8EEF5), width: 1.2),
            boxShadow: [
              BoxShadow(
                color: const Color(0xFF0F172A).withOpacity(0.02),
                blurRadius: 10,
                offset: const Offset(0, 4),
              ),
            ],
          ),
          child: Padding(
            padding: const EdgeInsets.all(20),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Container(
                      width: 36,
                      height: 36,
                      decoration: BoxDecoration(color: iconBg, borderRadius: BorderRadius.circular(8)),
                      alignment: Alignment.center,
                      child: Icon(iconData, color: iconCol, size: 20),
                    ),
                    const Icon(Icons.more_horiz, color: Color(0xFF94A3B8), size: 20),
                  ],
                ),
                const Spacer(),
                Text(
                  sala.name,
                  style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold, color: AppColors.blackBlue, fontFamily: 'Poppins'),
                ),
                const Spacer(),
                const Divider(color: Color(0xFFF1F5F9), height: 1, thickness: 1),
                const SizedBox(height: 12),
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Text('CÓDIGO', style: TextStyle(fontSize: 8, fontWeight: FontWeight.bold, color: Color(0xFF94A3B8), letterSpacing: 0.8, fontFamily: 'Poppins')),
                        const SizedBox(height: 2),
                        Text(sala.code ?? 'N/A', style: const TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: AppColors.blackBlue, fontFamily: 'Poppins')),
                      ],
                    ),
                    Column(
                      crossAxisAlignment: CrossAxisAlignment.end,
                      children: [
                        const Text('CAPACIDADE', style: TextStyle(fontSize: 8, fontWeight: FontWeight.bold, color: Color(0xFF94A3B8), letterSpacing: 0.8, fontFamily: 'Poppins')),
                        const SizedBox(height: 2),
                        Text('${sala.capacity ?? 0}', style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: AppColors.lightBlue, fontFamily: 'Poppins')),
                      ],
                    ),
                  ],
                ),
              ],
            ),
          ),
        );
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.transparent,
      body: ValueListenableBuilder<SalasState>(
        valueListenable: _controller,
        builder: (BuildContext context, SalasState state, Widget? child) {
          if (state.isLoading) {
            return const Center(child: CircularProgressIndicator());
          }
          if (state.errorMessage != null) {
            return Center(
              child: Text(state.errorMessage!, style: const TextStyle(color: Colors.red)),
            );
          }

          final List<Sala> currentList = state.salas;

          return Padding(
            padding: const EdgeInsets.symmetric(horizontal: 40, vertical: 32),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Text(
                          'Salas',
                          style: TextStyle(fontSize: 32, fontWeight: FontWeight.bold, color: AppColors.blackBlue, fontFamily: 'Poppins'),
                        ),
                        const SizedBox(height: 4),
                        Text(
                          '${currentList.length} salas ativas',
                          style: const TextStyle(fontSize: 14, color: AppColors.textSecondary, fontFamily: 'Poppins'),
                        ),
                      ],
                    ),
                    Row(
                      children: [
                        _buildViewToggle(),
                        const SizedBox(width: 12),
                        ImportExcelButton(
                          entidade: EntidadeImportacao.salas,
                          importarExcelUseCase: context.read<ImportarExcelUseCase>(),
                          onImported: _controller.fetchSalas,
                        ),
                        const SizedBox(width: 12),
                        ElevatedButton(
                          onPressed: _showNewSalaBottomSheet,
                          style: ElevatedButton.styleFrom(
                            backgroundColor: AppColors.blackBlue,
                            foregroundColor: Colors.white,
                            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                            padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 14),
                            elevation: 0,
                          ),
                          child: const Text('Nova Sala', style: TextStyle(fontWeight: FontWeight.w600, fontFamily: 'Poppins')),
                        ),
                      ],
                    ),
                  ],
                ),
                const SizedBox(height: 32),
                Expanded(
                  child: currentList.isEmpty
                      ? const Center(
                          child: Text(
                            'Nenhuma sala encontrada.',
                            style: TextStyle(fontSize: 16, color: AppColors.textSecondary, fontFamily: 'Poppins'),
                          ),
                        )
                      : (_isListView ? _buildListView(currentList) : _buildGridView(currentList)),
                ),
              ],
            ),
          );
        },
      ),
    );
  }
}
